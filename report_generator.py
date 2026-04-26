"""
Gerador de Relatórios Avançados

Gera relatórios em HTML, JSON e opcionalmente PDF.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from Virus_project import ScanResult


class HTMLReportGenerator:
    """Gera relatórios em formato HTML."""

    HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-PT">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Varredura - Antivírus</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        header h1 {{
            font-size: 28px;
            margin-bottom: 5px;
        }}
        header p {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f5f5f5;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }}
        .stat-value.clean {{ color: #4caf50; }}
        .stat-value.infected {{ color: #f44336; }}
        .stat-value.skipped {{ color: #ff9800; }}
        .content {{
            padding: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th {{
            background: #f5f5f5;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #ddd;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}
        tr:hover {{
            background: #f9f9f9;
        }}
        .status {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            text-align: center;
        }}
        .status.clean {{
            background: #c8e6c9;
            color: #2e7d32;
        }}
        .status.infected {{
            background: #ffcdd2;
            color: #c62828;
        }}
        .status.skip {{
            background: #ffe0b2;
            color: #e65100;
        }}
        .threat {{ color: #f44336; font-weight: 600; }}
        .hash {{ font-family: 'Courier New', monospace; font-size: 11px; }}
        footer {{
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #ddd;
        }}
        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🛡️ Relatório de Varredura</h1>
            <p>Antivírus Projeto v1.0 | {scan_date}</p>
        </header>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">Total Analisado</div>
                <div class="stat-value">{total}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Ficheiros Limpos</div>
                <div class="stat-value clean">{clean}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Infectados</div>
                <div class="stat-value infected">{infected}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Ignorados</div>
                <div class="stat-value skipped">{skipped}</div>
            </div>
        </div>

        <div class="content">
            {threat_section}
            {summary_section}
        </div>

        <footer>
            <p>© 2024 Antivírus Projeto | Relatório gerado automaticamente</p>
        </footer>
    </div>
</body>
</html>"""

    THREAT_TABLE = """
            <h2>⚠️ Ameaças Detectadas</h2>
            <table>
                <thead>
                    <tr>
                        <th>Ficheiro</th>
                        <th>Ameaça</th>
                        <th>Hash SHA256</th>
                    </tr>
                </thead>
                <tbody>
                    {threat_rows}
                </tbody>
            </table>"""

    THREAT_ROW = """<tr>
                        <td>{file_path}</td>
                        <td><span class="threat">{reason}</span></td>
                        <td><span class="hash">{sha256}</span></td>
                    </tr>"""

    SUMMARY_TABLE = """
            <h2>📊 Resumo Detalhado</h2>
            <table>
                <thead>
                    <tr>
                        <th>Ficheiro</th>
                        <th>Estado</th>
                        <th>Hash</th>
                    </tr>
                </thead>
                <tbody>
                    {summary_rows}
                </tbody>
            </table>"""

    SUMMARY_ROW = """<tr>
                        <td>{file_path}</td>
                        <td><span class="status {status_class}">{status}</span></td>
                        <td><span class="hash">{sha256}</span></td>
                    </tr>"""

    @staticmethod
    def generate(
        results: List[ScanResult],
        output_file: Path = Path("output/scan_report.html"),
        include_summary: bool = True,
    ) -> bool:
        """Gera relatório HTML."""
        try:
            infected = [r for r in results if r.status == "infected"]
            clean = [r for r in results if r.status == "clean"]
            skipped = [r for r in results if r.status == "skip"]

            threat_rows = ""
            for item in infected:
                threat_rows += HTMLReportGenerator.THREAT_ROW.format(
                    file_path=item.file_path,
                    reason=item.reason,
                    sha256=item.sha256[:32] + "..." if len(item.sha256) > 32 else item.sha256,
                )

            threat_section = ""
            if infected:
                threat_section = HTMLReportGenerator.THREAT_TABLE.format(threat_rows=threat_rows)

            summary_section = ""
            if include_summary:
                summary_rows = ""
                for item in results[:50]:
                    status_class = "clean" if item.status == "clean" else ("infected" if item.status == "infected" else "skip")
                    summary_rows += HTMLReportGenerator.SUMMARY_ROW.format(
                        file_path=item.file_path,
                        status=item.status.upper(),
                        status_class=status_class,
                        sha256=item.sha256[:24] + "..." if item.sha256 else "N/A",
                    )

                summary_section = HTMLReportGenerator.SUMMARY_TABLE.format(
                    summary_rows=summary_rows + (f"<tr><td colspan='3' style='text-align: center; color: #999;'>{len(results) - 50} mais resultados...</td></tr>" if len(results) > 50 else "")
                )

            html = HTMLReportGenerator.HTML_TEMPLATE.format(
                scan_date=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                total=len(results),
                clean=len(clean),
                infected=len(infected),
                skipped=len(skipped),
                threat_section=threat_section,
                summary_section=summary_section,
            )

            output_file.parent.mkdir(parents=True, exist_ok=True)
            with output_file.open("w", encoding="utf-8") as f:
                f.write(html)

            return True
        except Exception as e:
            print(f"Erro ao gerar relatório HTML: {e}")
            return False


def generate_json_report(
    results: List[ScanResult],
    output_file: Path = Path("output/scan_report.json"),
) -> bool:
    """Gera relatório JSON."""
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {
                "file_path": r.file_path,
                "status": r.status,
                "reason": r.reason,
                "sha256": r.sha256,
            }
            for r in results
        ]
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao gerar relatório JSON: {e}")
        return False
