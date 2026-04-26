# Plano de Redesign Frontend — Anti-Virus Projeto
## De projeto escolar a produto profissional

> **Contexto:** Site estático em GitHub Pages (`index.html` único, CSS inline). Stack actual: HTML + CSS vanilla + zero JS. A estética dark/green é boa e deve ser mantida — o problema é execução, não identidade.

---

## 1. Diagnóstico do Estado Actual

### O que está bem
- Identidade visual coerente (dark background `#060a06` + neon green `#00ff88`)
- Tipografia com personalidade (Syne bold + Share Tech Mono)
- Terminal mockup na hero cria contexto imediato
- Grid de funcionalidades limpa
- URL pública funcional via GitHub Pages

### Problemas críticos
| Problema | Impacto | Prioridade |
|---|---|---|
| "Scanner Antivírus **em Python**" — O `em Python` na headline principal dilui a proposta de valor; "em Python" é detalhe de implementação, não benefício | Primeira impressão | P0 |
| Terminal é estático — sem animação de typewriter, parece lorem ipsum | Engagement | P0 |
| Sem menu mobile — nav oculta em <600px sem hamburger | Acessibilidade | P0 |
| Sem copy-to-clipboard nos blocos de código | UX | P1 |
| Funcionalidades sem ícones — `F-001` parece placeholder, não produto | Credibilidade | P1 |
| Sem scroll-triggered animations — tudo anima só no load | Dinamismo | P1 |
| Sem meta tags OG / Twitter Card | Partilha social | P1 |
| Roadmap plano — lista simples sem progressão visual | Narrativa | P2 |
| Sem social proof — estrelas GitHub, nº de ficheiros scaneados, etc. | Confiança | P2 |
| Sem secção "Como funciona" técnica — arquitectura invisível | Profundidade | P2 |
| Sem preview da GUI (screenshots de `gui.py`) | Demonstração | P2 |
| Fonte carregada de Google Fonts CDN — FOUT potencial | Performance | P3 |
| Sem `prefers-reduced-motion` — animações forçadas | Acessibilidade | P3 |

---

## 2. Design System 2026

### Filosofia
**"Cyber-Minimal"** — A estética de terminal hacker é o core, mas tratada com disciplina de produto. Nada de decoração por decoração. Cada elemento visual serve uma função de comunicação.

### Paleta de cores (tokens CSS)
```css
:root {
  /* Core */
  --green-500: #00ff88;        /* accent principal — CTAs, highlights */
  --green-400: #33ffaa;        /* hover states */
  --green-600: #00cc66;        /* pressed states */
  --green-900: #003320;        /* backgrounds de destaque */

  /* Backgrounds (escala de profundidade) */
  --bg-base:    #060a06;       /* fundo de página */
  --bg-raised:  #0d140d;       /* cards, terminais */
  --bg-overlay: #111811;       /* nav, tooltips */
  --bg-subtle:  #1a2e1a;       /* separadores, hover subtle */

  /* Semânticas */
  --danger:  #ff4444;          /* infectado / erro */
  --warning: #ffaa00;          /* pendente / aviso */
  --info:    #00aaff;          /* informação / progresso */
  --success: #00ff88;          /* limpo / ok */

  /* Texto */
  --text-primary:   #e8f5e8;   /* corpo de texto */
  --text-secondary: #8fa88f;   /* labels, captions */
  --text-muted:     #5a7a5a;   /* placeholders, bordas */

  /* Bordas */
  --border-subtle:  rgba(0,255,136,0.08);
  --border-default: rgba(0,255,136,0.15);
  --border-strong:  rgba(0,255,136,0.35);

  /* Glow */
  --glow-sm: 0 0 8px rgba(0,255,136,0.2);
  --glow-md: 0 0 20px rgba(0,255,136,0.3);
  --glow-lg: 0 0 40px rgba(0,255,136,0.15), 0 0 80px rgba(0,255,136,0.05);
}
```

### Tipografia
```css
/* Escala modular 1.25 (Major Third) */
--text-xs:   0.64rem;    /* 10.24px — labels mono */
--text-sm:   0.8rem;     /* 12.8px  — captions */
--text-base: 1rem;       /* 16px    — corpo */
--text-lg:   1.25rem;    /* 20px    — subtítulos */
--text-xl:   1.563rem;   /* 25px    — títulos secção */
--text-2xl:  1.953rem;   /* 31px */
--text-3xl:  2.441rem;   /* 39px */
--text-hero: clamp(2.5rem, 7vw, 5.5rem);  /* headline */

/* Famílias */
--font-display: 'Syne', sans-serif;        /* headlines, botões */
--font-mono:    'Share Tech Mono', monospace; /* terminal, código, labels */
```

### Espaçamento (escala 4px base)
```css
--space-1:  4px   --space-4:  16px  --space-8:  32px
--space-2:  8px   --space-5:  20px  --space-10: 40px
--space-3:  12px  --space-6:  24px  --space-16: 64px
```

### Animações
```css
/* Timing functions — evitar linear */
--ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
--ease-in-expo:  cubic-bezier(0.7, 0, 0.84, 0);
--ease-spring:   cubic-bezier(0.34, 1.56, 0.64, 1);  /* overshoots levemente */

/* Durações */
--duration-fast:   150ms;   /* hover, focus */
--duration-normal: 300ms;   /* transições de estado */
--duration-slow:   600ms;   /* scroll-reveal */
--duration-slower: 1000ms;  /* hero entrance */

/* Regra obrigatória de acessibilidade */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 3. Arquitectura de Componentes

```
index.html
├── <head>
│   ├── Meta tags SEO + OG + Twitter Card
│   ├── Preconnect para fontes
│   ├── Link fontes com font-display: swap
│   └── Structured Data (JSON-LD)
│
├── <nav> — Barra de navegação sticky com scroll indicator
├── <main>
│   ├── #hero — Hero section com terminal animado
│   ├── #stats — Contadores animados (scroll-triggered)
│   ├── #funcionalidades — Feature cards com ícones SVG
│   ├── #como-funciona — Diagrama de arquitectura visual
│   ├── #instalacao — Tabs Windows/Linux/macOS + clipboard
│   ├── #gui-preview — Screenshots/mockup da GUI Tkinter
│   ├── #roadmap — Timeline vertical com fases
│   └── #cta — Secção de conversão final
└── <footer> — Rodapé rico
```

---

## 4. Secção por Secção — Especificação Detalhada

---

### 4.1 `<head>` — Meta & Performance

**Problema actual:** Sem OG tags, sem Twitter card, sem structured data. Quando partilhado no LinkedIn ou Discord aparece sem preview.

**Implementação:**
```html
<!-- SEO -->
<meta name="description" content="Scanner antivírus open-source em Python. Detecção por SHA-256, quarentena automática, GUI incluída. Sem dependências externas.">
<meta name="keywords" content="antivírus, python, scanner, malware, sha256, clamav, open-source, cibersegurança">
<meta name="author" content="Nelson M Madeira Rijo">

<!-- Open Graph (LinkedIn, Facebook, Discord) -->
<meta property="og:title" content="Scanner Antivírus — Python Security Tool">
<meta property="og:description" content="Detecção de malware por SHA-256 + GUI gráfica + quarentena automática. Open-source, zero dependências.">
<meta property="og:image" content="https://nekas1980.github.io/anti-virus-projeto/og-image.png">
<meta property="og:url" content="https://nekas1980.github.io/anti-virus-projeto/">
<meta property="og:type" content="website">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Scanner Antivírus — Python Security Tool">
<meta name="twitter:image" content="https://nekas1980.github.io/anti-virus-projeto/og-image.png">

<!-- Performance -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="dns-prefetch" href="https://api.github.com">

<!-- Structured Data -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Scanner Antivírus",
  "applicationCategory": "SecurityApplication",
  "operatingSystem": "Windows, Linux, macOS",
  "offers": { "@type": "Offer", "price": "0", "priceCurrency": "EUR" },
  "author": { "@type": "Person", "name": "Nelson M Madeira Rijo" },
  "url": "https://github.com/Nekas1980/anti-virus-projeto",
  "license": "https://opensource.org/licenses/MIT"
}
</script>
```

**OG Image (og-image.png):** Gerar uma imagem 1200×630px estática com o terminal mockup sobre fundo dark. Pode ser criada em Figma ou com `node-canvas` num script de geração. Alternativa: serviço como `og-image.vercel.app`.

---

### 4.2 `<nav>` — Navegação

**Problemas actuais:**
- Nav links desaparecem em mobile (`display: none` sem alternativa)
- Nenhum feedback de secção activa durante scroll
- Nenhum indicador visual de progresso de leitura

**Design:**
```
┌─────────────────────────────────────────────────────────┐
│ // PROJETO-ANTIVIRUS     [GitHub ★ 42]  [≡] mobile     │
├─────────────────────────────────────────────────────────┤
│ ████████░░░░░░░░░░░░░░░░░░░░░  ← scroll progress bar   │
└─────────────────────────────────────────────────────────┘
```

**Comportamento:**
- Desktop: links horizontais com underline animado no hover e estado activo (calculado por IntersectionObserver)
- Mobile (< 768px): hamburger button (3 linhas → X animado) que abre um drawer/menu vertical com backdrop blur
- Scroll progress bar: linha de 2px no topo da nav, preenche da esquerda para direita com `scrollY / (documentHeight - viewportHeight)`
- GitHub Stars: fetch lazy de `https://api.github.com/repos/Nekas1980/anti-virus-projeto` → mostrar `stargazers_count` com ícone ★. Fallback gracioso se a API falhar (esconder o badge, não mostrar "undefined")

**Animação hamburger:**
```css
/* As 3 linhas transformam-se em X */
.hamburger.open .line-1 { transform: rotate(45deg) translate(5px, 5px); }
.hamburger.open .line-2 { opacity: 0; transform: scaleX(0); }
.hamburger.open .line-3 { transform: rotate(-45deg) translate(5px, -5px); }
```

---

### 4.3 `#hero` — Secção Principal

**Problemas actuais:**
- "em Python" na headline é detalhe de implementação, não proposta de valor
- Subtítulo muito técnico logo na abertura
- Terminal estático parece mockup de Figma

**Nova headline:**
```
Protege o teu sistema.          ← linha 1: verbo de acção
Código aberto.                  ← linha 2: diferenciador
Zero instalações.               ← linha 3: benefício-chave
```
*(Cada linha entra com animação sequencial — slide-up + fade, delay de 0.15s entre linhas)*

**Ou alternativa mais concisa:**
```
Scanner de
Malware
Sem Barreiras.
```
com `Malware` em `var(--green-500)`.

**Subtítulo (abaixo dos botões):**
> Detecção SHA-256 · Quarentena automática · GUI incluída · Python puro

*(chips/badges horizontais em vez de parágrafo — mais scannável)*

**OS Badges (novo elemento):**
```
[🪟 Windows]  [🐧 Linux]  [🍎 macOS]
```
Pequenos badges clicáveis que fazem anchor para a secção de instalação filtrada ao OS correspondente.

**Terminal animado (a grande melhoria):**

Em vez de HTML estático, implementar typewriter com JavaScript:
```javascript
const lines = [
  { text: 'PS> python Virus_project.py', class: 't-cmd', delay: 0 },
  { text: 'Diretório: C:\\Users\\Nelson\\Downloads', class: 't-out', delay: 800 },
  { text: '', delay: 400 },
  { text: 'A analisar 247 ficheiros...', class: 't-out', delay: 600 },
  { text: '✓ Limpos: 246', class: 't-clean', delay: 1200 },
  { text: '✗ Infectados: 1', class: 't-infected', delay: 400 },
  { text: '', delay: 300 },
  { text: '[INFECTADO] malware_sample.exe', class: 't-infected', delay: 500 },
  { text: '         → Trojan.Backdoor.Sim', class: 't-out', delay: 200 },
  { text: '', delay: 400 },
  { text: 'Mover para quarentena? (s/n): s', class: 't-warn', delay: 600 },
  { text: '✓ Quarentena concluída.', class: 't-done', delay: 800 },
  { text: 'Relatório: output/scan_report.json', class: 't-out', delay: 300 },
];
```

Cada linha aparece com velocidade de typing realista (caractere a caractere, ~30ms/char, com variação aleatória ±10ms para parecer humano). Após completar, o loop reinicia silenciosamente com fade-out/fade-in.

**Tab switcher no terminal (bónus):**
```
[CLI]  [GUI]  [API]    ← tabs no topo do terminal
```
Cada tab mostra um cenário diferente de uso — CLI, a GUI (screenshot), chamada de API futura. Mostra versatilidade do projecto.

---

### 4.4 `#stats` — Contadores de Impacto (nova secção)

**Propósito:** Criar credibilidade e escala com números concretos. Inserida entre hero e features.

**Layout:**
```
┌──────────┬──────────┬──────────┬──────────┐
│  10 000+ │   100%   │   0      │   MIT    │
│  ficheiros│  Python  │ deps ext.│  Licença │
│  testados│  puro    │          │          │
└──────────┴──────────┴──────────┴──────────┘
```

**Animação:** Quando o utilizador faz scroll até esta secção (IntersectionObserver), os números fazem count-up animation de 0 até ao valor final. Duração: 1.5s com easing `ease-out-expo`.

```javascript
function animateCounter(el, target, duration = 1500) {
  const start = performance.now();
  const update = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 4); // ease-out-quart
    el.textContent = Math.round(ease * target).toLocaleString('pt-PT');
    if (progress < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}
```

---

### 4.5 `#funcionalidades` — Feature Cards

**Problemas actuais:**
- `F-001`, `F-002`... parece wireframe, não produto final
- Sem ícones — parede de texto
- Hover effect subtil demais (só muda o `background`)
- 6 features em grid — podia ser expandido com mais detalhes

**Nova estrutura por card:**
```
┌─────────────────────────────┐
│  [ícone SVG 32×32]          │
│                             │
│  Detecção SHA-256           │  ← título em bold
│                             │
│  Calcula a impressão        │  ← descrição (2-3 linhas)
│  digital única de cada      │
│  ficheiro e compara com...  │
│                             │
│  ─────────────────          │  ← separador subtil
│  [→ Saber mais]             │  ← link para docs (opcional)
└─────────────────────────────┘
```

**Ícones SVG inline** (mantêm a estética, sem dependência de icon library):
- `F-001` Detecção SHA-256 → ícone de fingerprint / hash `#`
- `F-002` Scan Recursivo → ícone de pasta com seta recursiva
- `F-003` Quarentena → ícone de escudo com cadeado
- `F-004` Relatório JSON → ícone de documento `{ }`
- `F-005` Zero Dependências → ícone de cubo isolado / módulo
- `F-006` Open Source → ícone de código `< />`

**Efeito hover** (novo — micro-interaction):
```css
.feature-card {
  border: 1px solid var(--border-subtle);
  transition: border-color 300ms, box-shadow 300ms, transform 200ms;
}
.feature-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--glow-sm), inset 0 0 30px rgba(0,255,136,0.03);
  transform: translateY(-2px);
}
/* Ícone SVG anima ligeiramente no hover do card */
.feature-card:hover .feature-icon {
  filter: drop-shadow(0 0 8px var(--green-500));
  transform: scale(1.1);
}
```

**Scroll reveal:** Cada card entra em sequência quando o utilizador chega à secção (stagger de 80ms entre cards).

---

### 4.6 `#como-funciona` — Arquitectura Visual (nova secção)

**Propósito:** Mostrar a profundidade técnica do projecto. Essencial para developers e recrutadores.

**Diagrama de fluxo horizontal:**
```
┌──────────┐    ┌──────────────┐    ┌───────────────┐    ┌──────────────┐
│  Diretório│───▶│ SHA-256      │───▶│ Base de       │───▶│  Relatório   │
│  Alvo    │    │ Hash Engine  │    │ Assinaturas   │    │  JSON        │
└──────────┘    └──────────────┘    └───────────────┘    └──────────────┘
                                           │ match?
                                           ▼
                                    ┌───────────────┐
                                    │  Quarentena   │
                                    │  Automática   │
                                    └───────────────┘
```

Cada bloco é um `<div>` estilizado, as setas são SVG ou CSS borders. Animação: blocos e setas aparecem em sequência quando em viewport (IntersectionObserver).

**Abaixo do diagrama** — accordion técnico com 3 items:
- `► Como funciona o SHA-256` — explicação em 2 linhas + snippet de código
- `► Formato do ficheiro de assinaturas` — JSON de exemplo
- `► Formato do relatório gerado` — JSON de exemplo

---

### 4.7 `#instalacao` — Instalação com Tabs + Clipboard

**Problemas actuais:**
- 4 steps lineares sem código copiável
- Não considera múltiplos sistemas operativos
- Sem feedback visual de sucesso ao copiar

**Nova estrutura com tabs:**
```
┌────────────────────────────────────────────────────┐
│  [🪟 Windows]  [🐧 Linux / macOS]                 │
├────────────────────────────────────────────────────┤
│  Passo 1 — Clonar                                  │
│  ┌──────────────────────────────────────────┐      │
│  │ git clone https://github.com/...         │ [📋] │
│  └──────────────────────────────────────────┘      │
│                                                    │
│  Passo 2 — Verificar Python                        │
│  ┌──────────────────────────────────────────┐      │
│  │ python --version  # Requer 3.8+          │ [📋] │
│  └──────────────────────────────────────────┘      │
│                                                    │
│  Passo 3 — Executar                                │
│  ┌──────────────────────────────────────────┐      │
│  │ python Virus_project.py                  │ [📋] │
│  └──────────────────────────────────────────┘      │
│                                                    │
│  Passo 3b — GUI (opcional)                         │
│  ┌──────────────────────────────────────────┐      │
│  │ python gui.py                            │ [📋] │
│  └──────────────────────────────────────────┘      │
└────────────────────────────────────────────────────┘
```

**Clipboard implementation:**
```javascript
async function copyToClipboard(text, btn) {
  await navigator.clipboard.writeText(text);
  btn.textContent = '✓ Copiado!';
  btn.style.color = 'var(--green-500)';
  setTimeout(() => {
    btn.textContent = '📋';
    btn.style.color = '';
  }, 2000);
}
```

---

### 4.8 `#gui-preview` — Preview da Interface Gráfica (nova secção)

**Propósito:** `gui.py` existe e é uma funcionalidade completa — completamente ausente no site actual. Mostrá-la é imediato valor acrescentado.

**Opções (por ordem de esforço):**
1. **Screenshot real** — correr `gui.py`, tirar screenshot da janela Tkinter, optimizar em WebP
2. **Mockup HTML/CSS** — replicar o aspecto da GUI em CSS puro (mais flexível, sem ficheiro de imagem)
3. **GIF animado** — gravar screen recording do scan em tempo real

**Layout sugerido:**
```
┌─────────────────────────────────────────────────────┐
│  "Não só linha de comandos —                        │
│   também tens interface gráfica."                   │
│                                                     │
│  ┌─────────────────────────────────────────┐        │
│  │ // SCANNER ANTIVÍRUS         v1.0-Python│        │
│  │─────────────────────────────────────────│        │
│  │ DIRETÓRIO  [/home/user/Downloads  ] [📁]│        │
│  │ [SCAN PASTA] [SCAN RÁPIDO] [SCAN PC]   │        │
│  │ TOTAL: 247  LIMPOS: 246  INFECTADOS: 1 │        │
│  │─────────────────────────────────────────│        │
│  │ LOG EM TEMPO REAL                       │        │
│  │ ████████████████░░░░ 82% — 203/247     │        │
│  │ [✓] documento.pdf — limpo              │        │
│  │ [✗] malware.exe — Trojan.Backdoor.Sim  │        │
│  └─────────────────────────────────────────┘        │
│                                                     │
│  [Descarregar e correr]  [Ver gui.py no GitHub]    │
└─────────────────────────────────────────────────────┘
```

O mockup acima pode ser feito 100% em HTML/CSS, pixel-a-pixel a replicar a GUI Tkinter, sem imagens.

---

### 4.9 `#roadmap` — Timeline Vertical

**Problemas actuais:**
- Lista simples de badges + texto sem estrutura de progressão
- Não reflecte a profundidade do roadmap real (que vai até Phase 12 + long-term vision)

**Nova estrutura — Timeline vertical com fases agrupadas:**
```
●── FEITO ──────────────────────
│  ✓ Scanner SHA-256
│  ✓ Quarentena automática  
│  ✓ Relatório JSON
│  ✓ Interface GUI (Tkinter)
│
●── EM DESENVOLVIMENTO ─────────
│  ⟳ Actualização automática de assinaturas
│  ⟳ Integração VirusTotal API
│
●── PLANEADO ───────────────────
│  ○ Scan em tempo real (watchdog)
│  ○ Web Interface (FastAPI + React)
│  ○ Regras YARA
│
●── VISÃO A LONGO PRAZO ────────
│  ◇ Machine Learning detection
│  ◇ REST API server
│  ◇ Distributed scanning
│  ◇ Browser Extension
```

**Implementação CSS:**
- Linha vertical feita com `border-left: 2px solid var(--border-default)` no container
- Cada grupo tem um `●` posicionado absolutamente sobre a linha com cor correspondente (verde = feito, âmbar = em progresso, muted = planeado)
- Items "FEITO" têm `text-decoration: line-through` subtil com opacidade reduzida
- Hover num item mostra um tooltip com detalhes técnicos

---

### 4.10 `#cta` — Conversão Final

**Propósito:** Última secção antes do footer. Converter o visitor em utilizador/contribuidor.

**Layout:**
```
┌──────────────────────────────────────────────────────┐
│                                                      │
│  Pronto para começar?                                │
│                                                      │
│  Clona o repositório e testa em 3 minutos.          │
│                                                      │
│  ┌──────────────────────────────────────────┐        │
│  │ git clone https://github.com/Nekas1980/ │ [📋]   │
│  │ anti-virus-projeto.git                  │        │
│  └──────────────────────────────────────────┘        │
│                                                      │
│  [Ver no GitHub]  [Ler Documentação]                 │
│                                                      │
│  ★ Dá uma estrela se o projecto te ajudou           │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

### 4.11 `<footer>` — Rodapé Rico

**Problemas actuais:** 5 linhas minimalistas. Desperdiça espaço de credibilidade.

**Nova estrutura (3 colunas):**
```
┌───────────────┬─────────────────┬───────────────┐
│ // ANTI-VIRUS │ Navegação       │ Recursos       │
│ PROJECTO      │                 │                │
│               │ Funcionalidades │ GitHub ↗       │
│ Scanner de    │ Como usar       │ Documentação ↗ │
│ malware       │ Roadmap         │ Releases ↗     │
│ open-source.  │ GUI Preview     │ Issues ↗       │
│               │                 │                │
│ Nelson M.     │                 │ Licença MIT    │
│ Madeira Rijo  │                 │                │
├───────────────┴─────────────────┴───────────────┤
│ Python Bootcamp · IEFP 2026 · Cibersegurança    │
│ Feito com 🤍 em Faro, Portugal                   │
└─────────────────────────────────────────────────┘
```

---

## 5. JavaScript — Funcionalidades Interactivas

Todo o JS deve ser:
- Vanilla (sem frameworks — projecto estático simples)
- `defer` ou `type="module"` (não bloquear render)
- Fallback gracioso se JS estiver desactivado

### 5.1 IntersectionObserver — Scroll Animations
```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('animate-in');
      observer.unobserve(entry.target); // anima só uma vez
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('[data-animate]').forEach(el => observer.observe(el));
```

### 5.2 Active Nav Link — Highlight por secção
```javascript
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-links a');

const sectionObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      navLinks.forEach(link => {
        link.classList.toggle('active', link.hash === `#${entry.target.id}`);
      });
    }
  });
}, { rootMargin: '-40% 0px -40% 0px' });

sections.forEach(s => sectionObserver.observe(s));
```

### 5.3 Typewriter Terminal
- Fila de linhas com delay configurável por linha
- `setTimeout` encadeados (não `setInterval`)
- Cursor `|` pisca enquanto "escreve"
- Loop infinito com pausa de 3s no fim antes de reset
- Respeita `prefers-reduced-motion` (se activado, mostra o terminal final sem animação)

### 5.4 GitHub Stars Counter
```javascript
async function fetchGitHubStats() {
  try {
    const res = await fetch('https://api.github.com/repos/Nekas1980/anti-virus-projeto');
    const data = await res.json();
    document.getElementById('gh-stars').textContent = data.stargazers_count;
    document.getElementById('gh-forks').textContent = data.forks_count;
  } catch {
    document.getElementById('gh-badge').style.display = 'none'; // graceful fallback
  }
}
fetchGitHubStats();
```

### 5.5 Scroll Progress Bar
```javascript
window.addEventListener('scroll', () => {
  const scrolled = window.scrollY / (document.body.scrollHeight - window.innerHeight);
  document.getElementById('progress-bar').style.width = `${scrolled * 100}%`;
}, { passive: true });
```

### 5.6 Tab Switcher (Instalação)
```javascript
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const target = btn.dataset.tab;
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.hidden = true);
    btn.classList.add('active');
    document.getElementById(target).hidden = false;
  });
});
```

---

## 6. Responsividade — Breakpoints

```css
/* Mobile first */
/* base: 0px+ */

/* Tablet */
@media (min-width: 640px) {
  /* features grid: 2 colunas */
  /* terminal: padding maior */
}

/* Desktop pequeno */
@media (min-width: 1024px) {
  /* features grid: 3 colunas */
  /* nav: links visíveis, hamburger escondido */
  /* footer: 3 colunas */
}

/* Desktop grande */
@media (min-width: 1280px) {
  /* hero: layout 60/40 (texto + terminal lado a lado) */
  /* section max-width: 1100px centrado */
}
```

**Elementos críticos mobile:**
- Terminal: `font-size: 0.75rem`, scroll horizontal habilitado (`overflow-x: auto`)
- Feature cards: 1 coluna em mobile, 2 em tablet
- Steps: coluna única (sem grid de 2 colunas)
- Nav: hamburger com drawer full-width

---

## 7. Performance — Core Web Vitals

### LCP (Largest Contentful Paint) — alvo < 2.5s
- `<link rel="preload" as="font">` para Share Tech Mono (fonte do terminal — acima do fold)
- Imagem OG não afecta LCP da página, mas o terminal é above-the-fold
- Inline CSS crítico (above-the-fold) no `<style>`, carregar o resto async

### CLS (Cumulative Layout Shift) — alvo < 0.1
- Definir `width` e `height` em todos os elementos de imagem (GUI preview)
- `font-display: swap` nas Google Fonts
- Reservar espaço para o contador de GitHub Stars antes de carregar (`min-width: 2ch`)

### FID/INP (Interaction to Next Paint) — alvo < 200ms
- Event listeners `{ passive: true }` no scroll
- Typewriter com `requestAnimationFrame` em vez de `setInterval`
- Debounce no scroll progress bar

---

## 8. Acessibilidade

- `<nav aria-label="Navegação principal">`
- `<button aria-expanded="false" aria-controls="mobile-menu">` no hamburger
- `aria-live="polite"` no contador do terminal (actualiza dinamicamente)
- `aria-label="Copiar para área de transferência"` nos botões clipboard
- Foco visível em todos os elementos interactivos (`:focus-visible` ring verde)
- Contraste: `#00ff88` sobre `#060a06` = ratio 10.4:1 (excede AA e AAA)
- Skip-to-content link: `<a href="#hero" class="skip-link">Saltar para conteúdo</a>`
- `role="tab"`, `role="tablist"`, `role="tabpanel"` na secção de instalação

---

## 9. Plano de Implementação

### Fase 1 — Quick Wins (1-2h)
> Melhorias que não exigem refactor estrutural

- [ ] Corrigir headline hero (remover "em Python", melhorar copy)
- [ ] Adicionar meta tags OG + Twitter Card
- [ ] Adicionar `prefers-reduced-motion` ao CSS
- [ ] Adicionar menu hamburger mobile com CSS + JS mínimo
- [ ] Adicionar clipboard aos blocos de código existentes
- [ ] Adicionar `aria-label` aos elementos interactivos existentes
- [ ] Criar e adicionar `og-image.png`

### Fase 2 — Animações e Interactividade (2-3h)
- [ ] Implementar typewriter no terminal hero
- [ ] Implementar IntersectionObserver para scroll-reveal nas secções
- [ ] Implementar scroll progress bar na nav
- [ ] Implementar active nav link tracking
- [ ] Implementar GitHub Stars counter

### Fase 3 — Novas Secções (3-4h)
- [ ] Secção `#stats` com contadores animados
- [ ] Secção `#como-funciona` com diagrama de arquitectura
- [ ] Secção `#gui-preview` com mockup da GUI
- [ ] Redesign `#roadmap` para timeline vertical
- [ ] Secção `#cta` final

### Fase 4 — Polimento (1-2h)
- [ ] Feature cards com ícones SVG e efeitos hover melhorados
- [ ] Instalação com tabs Windows/Linux + clipboard
- [ ] Footer expandido com 3 colunas
- [ ] Stagger animations nos cards
- [ ] Teste cross-browser (Chrome, Firefox, Safari)
- [ ] Lighthouse audit (alvo: 95+ em todas as categorias)
- [ ] Teste de acessibilidade com axe DevTools

### Fase 5 — Deploy e Extras (1h)
- [ ] Verificar GitHub Actions deploy sem erros
- [ ] Testar no mobile (iOS Safari, Android Chrome)
- [ ] Submeter para Google Search Console
- [ ] Adicionar favicon SVG (escudo verde)

**Total estimado: 8-12 horas de implementação**

---

## 10. Ficheiros a criar/modificar

```
anti-virus-projeto/
├── index.html              ← SUBSTITUIÇÃO COMPLETA
├── assets/
│   ├── og-image.png        ← NOVO (1200×630px)
│   ├── favicon.svg         ← NOVO (escudo verde 32×32)
│   └── gui-preview.webp    ← NOVO (screenshot ou mockup da GUI)
└── .github/
    └── workflows/
        └── deploy.yml      ← SEM ALTERAÇÕES (já funciona)
```

O projecto deve continuar como **ficheiro único `index.html`** (sem build step) para manter a simplicidade do GitHub Pages. Todo o CSS e JS ficam inline ou em `<style>`/`<script>` no mesmo ficheiro.

---

## 11. Referências de Inspiração 2026

Projectos com estética similar bem executada:
- **Vercel** — animações de terminal, dark mode, micro-interactions
- **Linear** — motion design minimalista, scroll sequences
- **Raycast** — feature cards com ícones, copy-to-clipboard, dark theme
- **charm.sh** — estética de terminal/CLI, fonte mono, verde
- **Fig.io** (archivado) — CLI tool marketing page com terminal animado

---

*Plano criado em 2026-04-26 | Projecto: IEFP Python Bootcamp Cibersegurança Faro*
