<p align="center">
  <img src="./assets/banner.svg" alt="Mario Linares — Arquitecto de software. Frontend systems. Madrid." width="100%">
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Georgia&weight=400&size=20&duration=3500&pause=1400&color=C4A574&center=true&vCenter=true&width=720&height=36&lines=Arquitecturas+que+sobreviven+a+la+migraci%C3%B3n.;Sistemas+que+aguantan+inspecci%C3%B3n+y+planta.;Angular%2C+NestJS%2C+Nx+y+criterio." alt="Línea de enfoque">
</p>

<p align="center">
  <a href="mailto:mariolinaresparra@icloud.com"><img src="https://img.shields.io/badge/email-mariolinaresparra%40icloud.com-0b0f14?style=flat-square&labelColor=0b0f14&color=c4a574" alt="Email"></a>
  <a href="https://www.linkedin.com/in/mario-linares-131b84146"><img src="https://img.shields.io/badge/linkedin-mario--linares-0b0f14?style=flat-square&labelColor=0b0f14&color=7ba3c9" alt="LinkedIn"></a>
  <a href="https://github.com/mariolinares"><img src="https://img.shields.io/badge/github-mariolinares-0b0f14?style=flat-square&labelColor=0b0f14&color=3d9b8f" alt="GitHub"></a>
  <img src="https://img.shields.io/badge/madrid-españa-0b0f14?style=flat-square&labelColor=0b0f14&color=8b939e" alt="Madrid">
</p>

---

Diseño y construyo **sistemas frontend de larga vida**: microfrontends, monorepos y productos donde el detalle no es cosmética — es validez legal, tiempo real o dinero en tránsito.

Nueve años en producción. Banca (Santander, BNP Paribas, Evo), industria (frío, PLC, fotovoltaica), logística y restauración. Antes, diseño gráfico. Por eso el sistema se ve y se sostiene.

**Ahora:** arquitecto frontend en [VASS](https://www.vasscompany.com). En paralelo, producto propio — transporte, SCADA, rutas e IA que no sale de la red.

## En qué estoy

| | |
| :--- | :--- |
| **Portes** | SaaS de portes y documentación legal del transporte. Carta de Porte y DeCA. Back-office, PWA del conductor, API y custodia documental. |
| **Zunix** | Supervisión industrial de cámaras frigoríficas. Agente de planta, MQTT, TimescaleDB, alarmas e informes que encajan en un plan APPCC. |
| **ROUTES** | Optimización de rutas para distribución alimentaria: pedidos, VRP, revisión humana, app de conductor y un asistente RAG. |
| **VASS** | Arquitectura de microfrontends, librerías compartidas y migraciones Angular en banca. |

## Sistemas

Los repos que más me representan son privados. Aquí va lo que hay detrás, sin el código.

<table>
<tr>
<td width="50%" valign="top">

**Portes**<br>
SaaS de gestión de portes. Documentos que tienen que ser válidos ante una inspección, no solo “verse bien”. Monorepo Nx: Angular 21, PWA, NestJS, generación y custodia de PDF, URL pública de verificación.

`Angular` `NestJS` `Nx` `PWA`

</td>
<td width="50%" valign="top">

**Zunix Control**<br>
Cadena de frío con validez sanitaria. El registro certificado vive en el hardware; el software lee, alerta y presenta. Edge (FINS / Modbus), MQTT, TimescaleDB, SCADA web y un design system propio para planta.

`Angular 22` `NestJS` `MQTT` `Omron`

</td>
</tr>
<tr>
<td width="50%" valign="top">

**ROUTES**<br>
Ciclo completo de distribución: maestros, predicción, optimización VRP, despacho y monitorización. Web de planificación, app Ionic del conductor, API NestJS y un servicio Python para ML / RAG.

`Angular` `Ionic` `NestJS` `Python`

</td>
<td width="50%" valign="top">

**Vinolo**<br>
ERP + WMS + logística B2B. Diez bounded contexts, arquitectura DDD, ~95 tablas. El dominio manda; el framework no.

`NestJS` `Nx` `TypeORM` `DDD`

</td>
</tr>
<tr>
<td width="50%" valign="top">

**Sienta**<br>
Reservas, aforo y menú del día. Panel del restaurante, API con contrato OpenAPI y despliegue en Cloud Run. Producto pequeño, operación real.

`Angular` `NestJS` `Prisma` `GCP`

</td>
<td width="50%" valign="top">

**Iryo · Native Federation**<br>
Monorepo Nx de microfrontends Angular con deploys independientes: bookings, cambios, shell. La misma idea que llevo años aplicando en banca, sin el teatro del Module Federation clásico.

`Angular 19` `Nx` `Vite` `Federation`

</td>
</tr>
</table>

**También:** RAG corporativo 100 % local (NestJS + pgvector + Ollama), monitorización fotovoltaica, DApps y contratos Solidity (ETH / BSC), y un chat streaming sobre Angular.

## Cómo construyo

- **El dominio primero.** En Portes un campo mal puesto invalida un documento. En Zunix una lectura no se altera. La arquitectura sale de esa regla, no al revés.
- **Monorepo cuando hay sistema, no cuando hay moda.** Nx, contratos compartidos, fronts que pueden vivir con mock o con API.
- **Migrar sin parar el negocio.** Angular 4 → 14 en banca. Híbrido AngularJS + Angular cuando la coexistencia era la única vía.
- **Formar al equipo.** Pull requests, TDD, NgRx, RxJS. La arquitectura que no se enseña no se adopta.

## En producción

Arquitecto frontend en **VASS** (2021 — ). Antes, **Atmira** para BNP Paribas y Banco Santander, y **Babel** para Airbus.

- Microfrontends con Module Federation y Native Federation.
- Librerías custom con dependencias compartidas.
- Estrategia de testing (Karma, Jasmine, Jest, Cypress) y CI con Jenkins.
- Migraciones Angular y scripts para no hacerlas a mano dos veces.
- SSR, PWA, Angular Elements, Ionic / Capacitor.

## Caja de herramientas

<p>
  <img src="https://skillicons.dev/icons?i=typescript,angular,nestjs,nodejs,react,nx,rxjs,html,css,sass,tailwind,prisma,postgres,mongodb,docker,graphql,web3,solidity,python,git" alt="TypeScript, Angular, NestJS, Node, React, Nx, RxJS, HTML, CSS, Sass, Tailwind, Prisma, Postgres, MongoDB, Docker, GraphQL, Web3, Solidity, Python, Git">
</p>

| Capa | Lo que uso de verdad |
| :--- | :--- |
| Frontend | Angular (4 → 22), Signals, NgRx, RxJS, React, Ionic, SSR, PWA, Native Federation |
| Backend | NestJS, Node, TypeORM, Prisma, Strapi, JWT, OpenAPI |
| Datos y tiempo real | PostgreSQL, TimescaleDB, MongoDB, MQTT, Socket.IO, pgvector |
| Industria | Omron FINS, Modbus, SCADA, Node-RED, Sungrow / iSolarCloud |
| Plataforma | Nx, Docker, Vite, Cloudflare, Cloud Run, Jenkins |
| Cadena | Solidity, Ethers, Web3.js, Hardhat |

## Señal

<p align="center">
  <img height="160" src="https://github-readme-stats.vercel.app/api?username=mariolinares&show_icons=true&theme=github_dark&hide_border=true&bg_color=0b0f14&title_color=c4a574&icon_color=3d9b8f&text_color=c9d0d8&ring_color=c4a574" alt="Estadísticas de GitHub de Mario Linares">
  <img height="160" src="https://github-readme-stats.vercel.app/api/top-langs/?username=mariolinares&layout=compact&theme=github_dark&hide_border=true&bg_color=0b0f14&title_color=c4a574&text_color=c9d0d8" alt="Lenguajes más usados">
</p>

<p align="center">
  <img src="https://github-readme-streak-stats.herokuapp.com/?user=mariolinares&theme=dark&hide_border=true&background=0b0f14&ring=c4a574&fire=c4a574&currStreakLabel=c4a574&sideLabels=8b939e&dates=7d8794&stroke=1a2230" alt="Racha de contribuciones">
</p>

<p align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=mariolinares&theme=react-dark&bg_color=0b0f14&color=c4a574&line=3d9b8f&point=c4a574&area=true&hide_border=true&area_color=3d9b8f" alt="Gráfico de actividad">
</p>

## Hablar

Si tienes un sistema que hay que **ordenar, migrar o poner en planta** — no una landing — escríbeme.

<p>
  <a href="mailto:mariolinaresparra@icloud.com">mariolinaresparra@icloud.com</a>
  ·
  <a href="https://www.linkedin.com/in/mario-linares-131b84146">LinkedIn</a>
  ·
  Madrid
</p>
