<style>
  :root {
    --mint: #00ffa3;
    --bg: #030503;
  }
  
  /* Forçar override no Material Theme */
  .md-container, .md-main, .md-content, .md-sidebar {
    background-color: var(--bg) !important;
    color: #e8f5e8 !important;
    font-family: 'Share Tech Mono', monospace !important;
  }

  .md-header, .md-tabs {
    background-color: #0a0c0a !important;
    border-bottom: 1px solid rgba(0, 255, 163, 0.2) !important;
  }

  h1, h2, h3, .md-nav__link--active, .md-header__title {
    color: var(--mint) !important;
    text-shadow: 0 0 10px rgba(0, 255, 163, 0.3);
  }

  /* Efeito de scanline global */
  body::before {
    content: " ";
    display: block;
    position: fixed;
    top: 0; left: 0; bottom: 0; right: 0;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%), 
                linear-gradient(90deg, rgba(255, 0, 0, 0.02), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.02));
    z-index: 9999;
    background-size: 100% 4px, 3px 100%;
    pointer-events: none;
    opacity: 0.2;
  }

  .hero-container {
    padding: 3rem;
    border: 2px solid var(--mint);
    background: #000;
    margin: 2rem 0;
    position: relative;
    box-shadow: 0 0 20px rgba(0, 255, 163, 0.1);
  }

  .md-button--primary {
    background-color: var(--mint) !important;
    color: #000 !important;
    border-radius: 0 !important;
    font-weight: bold !important;
  }
</style>

# <span style="color: var(--mint);">[ SYSTEM_INIT ] :: CYBER-SENTINEL</span>

<div class="hero-container">
    <div style="font-family: 'Share Tech Mono', monospace;">
        <p style="color: var(--mint); margin-bottom: 0.5rem;">> LOADING CORE_MODULES...</p>
        <p style="color: var(--mint); margin-bottom: 2rem;">> STATUS: <span style="animation: blink 1s infinite;">STABLE</span></p>
        <h1 style="border: none; margin: 0; font-size: 3.5rem;">DEFESA_TOTAL</h1>
        <p style="color: #8fa88f; margin: 1.5rem 0;">Motor de varredura SHA-256 para integridade de sistemas distribuídos.</p>
        <div style="margin-top: 2rem;">
            <a href="guides/installation/" class="md-button md-button--primary">EXECUTAR_INSTALL</a>
        </div>
    </div>
</div>

## 🛠️ ESPECIFICAÇÕES_TÉCNICAS

- **ALGORITMO**: SHA-256 BIT_INTEGRITY
- **INTERFACE**: CUSTOM_TKINTER V2
- **DEPENDÊNCIAS**: ZERO_EXTERNAL_LIBS
- **LICENÇA**: MIT_OPEN_SOURCE

---
[ AUDIT_LOG: Nelson M Madeira Rijo ]
[ PROJECT_CODE: IEFP_BOOTCAMP_2026 ]

<script>
  console.log("Cyber-Sentinel UI Active...");
</script>
