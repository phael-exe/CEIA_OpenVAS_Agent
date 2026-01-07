# OpenVAS Agent: Your AI-Powered Vulnerability Analysis Copilot

![OpenVAS Agent Logo](openvasagent.png)

Welcome to the OpenVAS Agent project! This tool leverages the power of AI to revolutionize how you interact with the OpenVAS vulnerability scanner. Our goal is to create a powerful, intuitive copilot that assists you in analyzing vulnerabilities, interpreting results, and streamlining your security workflow.

## 🚀 Features

*   **AI-Powered Vulnerability Analysis:** Go beyond simple scans. The agent helps you understand the real-world impact of vulnerabilities.
*   **Intelligent Prioritization:** Automatically prioritize alerts based on severity, exploitability, and asset criticality.
*   **Actionable Remediation:** Receive best-practice remediation suggestions tailored to your specific environment.
*   **User-Friendly Interface:** Interact with OpenVAS through a simple, conversational interface.
*   **Customizable Workflows:** Adapt the agent to your unique security needs and scenarios.
*   **📊 CSV Analysis Module:** Analyze OpenVAS CSV reports with AI-powered insights and generate executive summaries.
*   **🌐 Streamlit Web Interface:** Interactive web dashboard for CSV analysis with charts and visualizations.
*   **🆓 Opensource LLM Support:** Use free models via Groq (Llama, Mixtral, Gemma) when you're out of OpenAI credits.

## 🔧 Getting Started

### Pre-requisites

*   An operational OpenVAS/Greenbone Vulnerability Management (GVM) instance.
*   Python 3.8 or higher.
*   Access to the GVM API.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/raphaelalvesdev/CEIA_OpenVAS_Agent
    cd CEIA_OpenVAS_Agent
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure your environment:**
    Create a `.env` file in the root directory of the project and add the following the informations of `ENV.md`

### Permissions

To allow the agent to connect to the `gvmd.sock` for API requests, you may need to adjust its permissions:

```bash
sudo chmod 660 /run/gvmd/gvmd.sock
```

If you still encounter issues, you can try a more permissive setting (use with caution):

```bash
sudo chmod 777 /run/gvmd/gvmd.sock
```

### Running the Agent

Launch the OpenVAS Agent with the following command:

```bash
python3 main.py
```

**New CSV Analysis Commands:**
- "Analise os CSVs" - Analyze all CSV files in csv_reports/
- "Lista os CSVs" - List available CSV files
- "Analise o arquivo X.csv" - Analyze specific CSV file

The agent now integrates CSV analysis capabilities! Just place your OpenVAS CSV reports in `csv_reports/` and ask the agent to analyze them.

### Running CSV Analysis

For detailed instructions on the CSV Analysis module, see [CSV_ANALYZER.md](docs/CSV_ANALYZER.md).

**Quick Start:**

1. **Via Streamlit Interface (Recommended):**
   ```bash
   streamlit run streamlit_app.py
   ```
   Access at `http://localhost:8501`

2. **Via Command Line:**
   ```bash
   # Place your CSV files in csv_reports/
   python src/tools/csv_analyzer.py
   ```
   Results will be saved in `csv_analysis_results/`

## 📂 Project Structure

```
.
├── .gitignore
├── ENV.md
├── LICENSE
├── main.py
├── streamlit_app.py          # Streamlit web interface for CSV analysis
├── openvasagent.png
├── README.md
├── requirements.txt
├── csv_reports/              # Place your OpenVAS CSV files here
├── csv_analysis_results/     # Generated reports are saved here
├── docs/
│   ├── CSV_ANALYZER.md       # CSV Analysis documentation
│   ├── diagram.html
│   └── Docs.md
└── src/
    ├── agents/
    │   ├── __init__.py
    │   ├── result_analyzer.py
    │   ├── supervisor.py
    │   └── task_creator.py
    ├── art/
    │   └── art.py
    ├── __pycache__/
    ├── state.py
    └── tools/
        ├── __init__.py
        ├── csv_analyzer.py   # CSV analysis module
        ├── gvm_results.py
        └── gvm_workflow.py
```

## 🤝 Contributing

We welcome contributions from the community! If you'd like to get involved, feel free to:

*   Report bugs and request features
*   Submit pull requests
*   Improve documentation

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📧 Contact

Have questions or feedback? Feel free to reach out to us at [rapha555lima@gmail.com](mailto:rapha555lima@gmail.com).