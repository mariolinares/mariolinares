"""Everything the profile says. Domains, never codenames; only measured numbers."""

HERO = {
    "label_left": "SHELL / MARIO LINARES",
    "label_right": "MADRID · 40.42° N 3.70° O",
    "name": ["Mario", "Linares"],
    "lead": "Arquitecto frontend. Diseño plataformas Angular que escalan con sus equipos.",
    "stack": ["Angular", "SSR", "Native Federation", "Nx", "Testing"],
    "daily_label": "USO DIARIO",
    # Simple Icons slugs, in reading order; names for the alt text.
    "daily": ["angular", "typescript", "nx", "reactivex", "ngrx", "nestjs", "nodedotjs", "vitest", "storybook", "docker"],
    "daily_names": ["Angular", "TypeScript", "Nx", "RxJS", "NgRx", "NestJS", "Node.js", "Vitest", "Storybook", "Docker"],
    "host": {"label": "HOST", "title": "shell", "sub": "ssr · edge"},
    # One route is live (signal); the rest load in turn (accent packets).
    "remotes": [
        {"id": "01", "name": "logística", "live": True},
        {"id": "02", "name": "rutas"},
        {"id": "03", "name": "industria"},
        {"id": "04", "name": "energía"},
        {"id": "05", "name": "ferroviario"},
        {"id": "06", "name": "ia aplicada"},
    ],
}

MODULES = {
    "index": "01",
    "title": "Lo que construyo",
    "note": "CÓDIGO PRIVADO · DEMO BAJO PETICIÓN",
    "cards": [
        {
            "id": "R / 01",
            "status": "EN PRODUCCIÓN",
            "live": True,
            "title": "Plataforma de logística",
            "body": "Transporte por carretera con documentos de control electrónicos válidos ante inspección. Back-office, PWA offline para conductores y conformidad automática.",
            "chips": ["Angular 21", "Nx", "NestJS", "Postgres RLS", "Vitest", "Playwright"],
            "metrics": [("16/16", "CONFORMIDAD"), ("83", "SPECS"), ("57k", "LÍNEAS TS")],
        },
        {
            "id": "R / 02",
            "status": "2026",
            "title": "Optimización de rutas",
            "body": "Reparto para distribución alimentaria: solver VRP, revisión humana, despacho y seguimiento en vivo. App de conductor que trabaja sin conexión.",
            "chips": ["Angular zoneless", "Ionic", "NestJS", "OR-Tools", "PostGIS"],
            "metrics": [("166", "PRS"), ("137", "SUITES TEST"), ("14", "ADR")],
        },
        {
            "id": "R / 03",
            "status": "2026",
            "title": "Monitorización industrial",
            "body": "Cadena de frío lista para inspección: PLC, agente edge con buffer local, MQTT, lecturas encadenadas por hash y SCADA en Angular.",
            "chips": ["Angular 22", "Nx", "TimescaleDB", "MQTT", "FINS · Modbus", "Storybook"],
            "metrics": [("19", "PROYECTOS NX"), ("163", "SPECS"), ("104k", "LÍNEAS TS")],
        },
        {
            "id": "R / 04",
            "status": "2026",
            "title": "Design system como código",
            "body": "Librería Angular de siete entry points para planta solar. La CI valida el paquete publicado: bundle, API pública, contraste AA y fronteras.",
            "chips": ["Angular 22", "Storybook 10", "Playwright", "nx release"],
            "metrics": [("162", "STORIES"), ("133", "SPECS"), ("7", "ENTRY POINTS")],
        },
        {
            "id": "R / 05",
            "status": "REFERENCIA",
            "title": "Micro-frontends federados",
            "body": "El monolito B2C de un operador ferroviario, partido en un shell y cuatro remotos de dominio con versionado y release independientes.",
            "chips": ["Native Federation", "nx release", "Storybook", "Verdaccio"],
            "metrics": [("4", "REMOTOS"), ("25", "COMPONENTES"), ("19", "STORIES")],
        },
        {
            "id": "R / 06",
            "status": "EN PRODUCCIÓN",
            "title": "SSR en el edge",
            "body": "Web corporativa con portal de empleo: prerender regenerado por el CMS, SSR cacheado en el edge e hidratación incremental.",
            "chips": ["@angular/ssr", "Cloudflare Workers", "Strapi", "Hydration"],
            "metrics": [("84", "COMMITS"), ("2", "MODOS RENDER"), ("18–20", "ANGULAR")],
        },
    ],
    "also_label": "TAMBIÉN",
    "also": [
        "RAG corporativo local con re-ranking",
        "Asistente con tool use sobre catálogo B2B",
        "SaaS de reservas con SSR híbrido",
        "Editor canvas con NgRx SignalStore",
        "SSR + Native Federation en servidor",
    ],
}

PRINCIPLES = {
    "index": "02",
    "title": "Cómo trabajo",
    "note": "PRINCIPIOS",
    "items": [
        ("01", "Fronteras explícitas", "Nx con tags de scope y tipo: cada librería sabe de quién puede depender, y la CI lo hace cumplir."),
        ("02", "Federar en runtime", "Native Federation con dependencias singleton: cada equipo despliega su remoto sin esperar al resto."),
        ("03", "Renderizar donde importa", "SSR, prerender e hidratación incremental para lo que indexa y convierte. El cliente, para lo demás."),
        ("04", "Tests como contrato", "Vitest en la lógica, Playwright en el flujo, Storybook con a11y en lo visual. Se prueba lo publicado."),
    ],
}

LAYERS = {
    "index": "03",
    "title": "Stack por capas",
    "note": "DE LA PETICIÓN AL DESPLIEGUE",
    "layers": [
        ("L / 01", "Render", ["@angular/ssr", "Hydration", "Prerender", "Cloudflare Workers", "PWA"]),
        ("L / 02", "Composición", ["Native Federation", "Module Federation", "Web Components", "Angular Elements"]),
        ("L / 03", "Aplicación", ["Angular", "TypeScript", "Signals", "RxJS", "NgRx", "Ionic"]),
        ("L / 04", "Calidad", ["Vitest", "Jest", "Playwright", "Cypress", "Storybook", "SonarQube"]),
        ("L / 05", "Plataforma", ["Nx", "NestJS", "PostgreSQL", "Docker", "Terraform", "Verdaccio"]),
    ],
}

TIMELINE = {
    "index": "04",
    "title": "Trayectoria",
    "note": "MADRID · DESDE 2017",
    "stations": [
        {"year": "2008", "role": "Diseño gráfico", "where": "Formación en publicidad"},
        {"year": "2017", "role": "Desarrollador frontend", "where": "Babel · para Airbus"},
        {"year": "2019", "role": "Arquitecto frontend", "where": "Atmira · Santander, BNP Paribas"},
        {"year": "2021", "role": "Arquitecto frontend", "where": "VASS · micro-frontends"},
        {"year": "HOY", "role": "NGINEER", "where": "Estudio propio · logística, industria, energía", "now": True},
    ],
}

CONTACT = {
    "label": "FIN DE RUTA",
    "title": ["Hablemos de fronteras,", "remotos y renderizado."],
    "rows": [
        ("CORREO", "mariolinaresparra@icloud.com"),
        ("LINKEDIN", "in/mario-linares-131b84146"),
        ("BASE", "Madrid"),
    ],
}

PUBLIC = {
    "experiments": [
        ("angularssr-host", "shell SSR que resuelve remotos federados en servidor"),
        ("angularssr-remote", "remoto federado con render en servidor"),
        ("angularnossr", "remoto solo cliente, con fallback en el host"),
    ],
    "email": "mariolinaresparra@icloud.com",
    "linkedin": "https://www.linkedin.com/in/mario-linares-131b84146",
}

# Chip label → Simple Icons slug. Labels with no entry stay text-only (no invented marks).
TECH_ICONS = {
    "Angular": "angular", "Angular 21": "angular", "Angular 22": "angular", "Angular zoneless": "angular",
    "@angular/ssr": "angular", "Angular Elements": "angular", "Signals": "angular",
    "TypeScript": "typescript", "Nx": "nx", "nx release": "nx", "RxJS": "reactivex", "NgRx": "ngrx",
    "NestJS": "nestjs", "Node.js": "nodedotjs", "Ionic": "ionic", "Strapi": "strapi",
    "Vitest": "vitest", "Jest": "jest", "Cypress": "cypress", "Storybook": "storybook", "Storybook 10": "storybook",
    "SonarQube": "sonarqubeserver", "PostgreSQL": "postgresql", "Postgres RLS": "postgresql", "PostGIS": "postgresql",
    "TimescaleDB": "timescale", "MQTT": "mqtt", "Docker": "docker", "Terraform": "terraform",
    "Verdaccio": "verdaccio", "Cloudflare Workers": "cloudflareworkers", "Web Components": "webcomponentsdotorg",
    "PWA": "pwa", "Module Federation": "webpack",
}

CLIENTS = {
    "index": "05",
    "title": "Con quién he trabajado",
    "note": "EMPRESAS Y CLIENTES",
    # (file stem under design/logos/clients, name for the alt text)
    "logos": [
        ("santander", "Banco Santander"),
        ("bnp-paribas", "BNP Paribas"),
        ("airbus", "Airbus"),
        ("bbva", "BBVA"),
        ("caixabank", "CaixaBank"),
        ("inditex", "Inditex"),
        ("iryo", "iryo"),
        ("pibank", "Pibank"),
        ("btravel", "B travel"),
        ("adeslas", "Adeslas"),
    ],
    "employers_label": "A TRAVÉS DE",
    "employers": ["VASS", "Atmira", "Babel", "NGINEER"],
}
