# openvas_agent

This repository have a goal of make a plan for integration of an AI with the OpenVAS API, aiming to eventually develop a copilot capable of assisting users in vulnerability analysis and result interpretation. The idea is that the tool could automate tasks such as prioritizing alerts, suggesting remediations based on best practices, and providing detailed explanations. This planning will consider challenges such as secure authentication, user-friendly response formatting, and the possibility of customizing the experience for specific user scenarios.

---

## **Requirements**

Install the necessary dependencies, use a virtual environment for this, and then install the dependencies in your virtual environment

 ```bash
   python3 -m .venv venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

Developer Interface for Greenbone Vulnerability Management(OpenVAS) API: https://greenbone.github.io/python-gvm/api/api.html

Make an .env file to storage sensible informations of your code, like OpenVAS user, password, OPENAI api key