/* Cliente web del Tres en Raya.
 *
 * Habla con la API Flask (api/app.py): crea partidas, envia jugadas y
 * recibe el estado. En los modos con IA muestra las metricas (nodos y
 * tiempo) y, en el modo ML, las reglas que el arbol se hizo para decidir.
 *
 * La segunda mitad dibuja el arbol de decision con D3: los nodos se
 * cargan desde /api/arbol y se expanden o colapsan con el clic.
 */

"use strict";

let partidaId = null;
let estado = null;
let ocupado = false;
let ultimaJugada = null;

const tableroEl = document.getElementById("tablero");
const menuEl = document.getElementById("menu");
const juegoEl = document.getElementById("juego");

const NOMBRES_MODOS = {
  hh: "Humano vs Humano",
  minimax: "Humano vs IA Minimax",
  ml: "Humano vs IA Machine Learning",
};

/* ---------- Comunicacion con la API ---------- */

async function api(ruta, opciones) {
  const respuesta = await fetch(ruta, {
    method: (opciones && opciones.metodo) || "GET",
    headers: { "Content-Type": "application/json" },
    body: opciones && opciones.cuerpo
      ? JSON.stringify(opciones.cuerpo) : undefined,
  });
  const datos = await respuesta.json();
  if (!respuesta.ok) {
    throw new Error(datos.error || "error del servidor");
  }
  return datos;
}

/* ---------- Pintado del juego ---------- */

function pintarTablero() {
  tableroEl.innerHTML = "";
  estado.tablero.forEach((fila, f) => {
    fila.forEach((valor, c) => {
      const boton = document.createElement("button");
      boton.className = "celda";
      boton.textContent = valor === " " ? "" : valor;
      if (valor === "X") boton.classList.add("ficha-x");
      if (valor === "O") boton.classList.add("ficha-o");
      if (ultimaJugada && ultimaJugada.fila === f
          && ultimaJugada.columna === c) {
        boton.classList.add("ultima");
      }
      if (estado.linea && estado.linea.some(
          ([lf, lc]) => lf === f && lc === c)) {
        boton.classList.add("ganadora");
      }
      boton.disabled = valor !== " " || estado.terminado || ocupado
        || (estado.modo !== "hh" && estado.turno !== "X");
      boton.addEventListener("click", () => jugar(f, c));
      tableroEl.appendChild(boton);
    });
  });
}

function pintarEstado() {
  pintarTablero();
  document.getElementById("modo-actual").textContent =
    NOMBRES_MODOS[estado.modo];
  const mensaje = document.getElementById("mensaje");
  const turno = document.getElementById("turno");
  if (estado.terminado) {
    turno.textContent = "";
    if (estado.ganador === "X") {
      mensaje.textContent = "Ganaste";
    } else if (estado.ganador === "O") {
      mensaje.textContent = "Gana la IA";
    } else {
      mensaje.textContent = "Empate";
    }
  } else {
    mensaje.textContent = "";
    turno.textContent = "Turno del jugador " + estado.turno;
  }
}

function pintarMetricas(info) {
  document.getElementById("metricas").classList.remove("oculto");
  document.getElementById("nodos").textContent = info.nodos;
  document.getElementById("tiempo").textContent = info.milisegundos;
}

function pintarReglas(reglas) {
  const caja = document.getElementById("caja-reglas");
  if (!reglas || reglas.length === 0) {
    caja.classList.add("oculto");
    return;
  }
  caja.classList.remove("oculto");
  const lista = document.getElementById("reglas");
  lista.innerHTML = "";
  reglas.forEach((regla) => {
    const item = document.createElement("li");
    item.textContent = regla;
    lista.appendChild(item);
  });
}

/* ---------- Flujo del juego ---------- */

async function nuevoJuego(modo) {
  estado = await api("/api/partidas", { metodo: "POST", cuerpo: { modo } });
  partidaId = estado.id;
  ultimaJugada = null;
  document.getElementById("metricas").classList.add("oculto");
  document.getElementById("caja-reglas").classList.add("oculto");
  menuEl.classList.add("oculto");
  juegoEl.classList.remove("oculto");
  pintarEstado();
}

async function jugar(fila, columna) {
  if (ocupado || !estado || estado.terminado) return;
  ocupado = true;
  pintarTablero();
  try {
    const respuesta = await api(
      "/api/partidas/" + partidaId + "/movimientos",
      { metodo: "POST", cuerpo: { fila, columna } });
    if (respuesta.ia) {
      pintarMetricas(respuesta.ia);
      pintarReglas(respuesta.ia.reglas);
      ultimaJugada = respuesta.ia.jugada;
    } else {
      ultimaJugada = null;
    }
    estado = respuesta.estado;
    pintarEstado();
    if (ultimaJugada) {
      setTimeout(() => {
        ultimaJugada = null;
        pintarTablero();
      }, 900);
    }
  } catch (e) {
    document.getElementById("mensaje").textContent = e.message;
  }
  ocupado = false;
  pintarTablero();
}

function volverAlMenu() {
  partidaId = null;
  estado = null;
  juegoEl.classList.add("oculto");
  menuEl.classList.remove("oculto");
}

document.querySelectorAll("button.modo").forEach((boton) => {
  boton.addEventListener("click", () => nuevoJuego(boton.dataset.modo));
});
document.getElementById("volver").addEventListener("click", volverAlMenu);

/* ---------- Arbol de decision con D3 ---------- */

const colores = d3.scaleOrdinal(d3.schemeTableau10);

function dibujarArbol(datos) {
  // Ids estables en los datos: sin esto D3 confunde los nodos al
  // expandir o colapsar ramas.
  let contador = 0;
  (function ponerIds(n) {
    n.id = contador++;
    (n.children || []).forEach(ponerIds);
  })(datos.raiz);

  const raiz = d3.hierarchy(datos.raiz);
  raiz.x0 = 0;
  raiz.y0 = 0;

  // Se empieza con solo la primera pregunta visible; el resto se
  // despliega con el clic. El arbol completo tiene 461 nodos.
  raiz.children.forEach(colapsar);

  const anchoNivel = 230;
  const altoNodo = 30;
  const niveles = 7;
  const svg = d3.select("#arbol").append("svg");
  const lienzo = svg.append("g");

  const zoom = d3.zoom().on("zoom", (evento) => {
    lienzo.attr("transform", evento.transform);
  });
  svg.call(zoom);

  function colapsar(nodo) {
    if (nodo.children) {
      nodo.children.forEach(colapsar);
      nodo._children = nodo.children;
      nodo.children = null;
    }
  }

  function actualizar() {
    const nodos = raiz.descendants();
    const enlaces = raiz.links();
    const alto = Math.max(420, nodos.length * altoNodo + 40);

    svg.attr("viewBox", [-80, 0, niveles * anchoNivel + 340, alto]);
    // Ancho fijo en pixeles: si la ventana es chica aparece scroll
    // horizontal en vez de encoger el arbol.
    svg.attr("width", niveles * anchoNivel + 340);

    // nodeSize fija el espacio por nivel: la profundidad d siempre esta
    // a d * anchoNivel del origen, se expandan o colapsen ramas.
    const layout = d3.tree().nodeSize([altoNodo, anchoNivel]);
    layout(raiz);

    // Centra verticalmente los nodos cuando el arbol visible es chico.
    const margenVertical =
      Math.max(0, (alto - nodos.length * altoNodo) / 2);

    // Enlaces: curvas horizontales de padre a hijo.
    lienzo.selectAll("path.enlace")
      .data(enlaces, (d) => d.target.data.id)
      .join("path")
      .attr("class", "enlace")
      .attr("fill", "none")
      .attr("stroke", "#4a5270")
      .attr("d", d3.linkHorizontal()
        .x((d) => d.y)
        .y((d) => d.x + 20 + margenVertical));

    // Nodos: circulo (clic para expandir) y texto con la pregunta.
    const nodo = lienzo.selectAll("g.nodo-arbol")
      .data(nodos, (d) => d.data.id)
      .join("g")
      .attr("class", "nodo-arbol")
      .attr("transform", (d) =>
        "translate(" + d.y + "," + (d.x + 20 + margenVertical) + ")");

    nodo.selectAll("circle").data((d) => [d]).join("circle")
      .attr("r", 7)
      .attr("fill", (d) => d.data.hoja
        ? colores(d.data.jugada)
        : (d._children ? "#febc2e" : "#8ab4ff"))
      .on("click", (evento, d) => {
        if (d.children) {
          d._children = d.children;
          d.children = null;
        } else {
          d.children = d._children;
          d._children = null;
        }
        actualizar();
      });

    nodo.selectAll("text").data((d) => [d]).join("text")
      .attr("dy", "0.32em")
      .attr("x", (d) => (d.depth === 0 ? 14
        : (d.children || d._children ? -14 : 14)))
      .attr("text-anchor", (d) => (d.depth === 0 ? "start"
        : (d.children || d._children ? "end" : "start")))
      .text((d) => d.data.nombre + " (" + d.data.muestras + ")");
  }

  actualizar();
}

document.getElementById("cargar-arbol").addEventListener("click",
  async function cargar() {
    this.disabled = true;
    this.textContent = "Entrenando el arbol...";
    try {
      const datos = await api("/api/arbol");
      document.getElementById("precision").classList.remove("oculto");
      document.getElementById("valor-precision").textContent =
        (datos.precision * 100).toFixed(1) + "%";
      dibujarArbol(datos);
      this.textContent = "Arbol cargado";
    } catch (e) {
      this.textContent = "Error: " + e.message;
      this.disabled = false;
    }
  });

// Abrir la pagina con #arbol carga el arbol directamente, util para
// compartir el enlace o para la demo en la defensa.
if (location.hash === "#arbol") {
  document.getElementById("cargar-arbol").click();
}
