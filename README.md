# OPENVAS AGENT

openvasagent.png

This repository have a goal of make a plan for integration of an AI with the OpenVAS API, aiming to eventually develop a copilot capable of assisting users in vulnerability analysis and result interpretation. The idea is that the tool could automate tasks such as prioritizing alerts, suggesting remediations based on best practices, and providing detailed explanations. This planning will consider challenges such as secure authentication, user-friendly response formatting, and the possibility of customizing the experience for specific user scenarios.

---

## **OpenVAS Instalation**

![Greenbone Logo](https://www.greenbone.net/wp-content/uploads/gb_new-logo_horizontal_rgb_small.png)

OpenVAS Install Guide: https://dev.iachieved.it/iachievedit/installing-greenbone-openvas-on-ubuntu-24-04/ (Ubuntu 24.04)
OpenVAS GitHub: https://github.com/greenbone/openvas-scanner 

For Kali Linux: 

```bash
   sudo apt install gvm
   ```
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

---

## **Requests**

To acess gvmd.sock to made an UnixSocketConnection to make requests for GVM API, try:

```bash
   sudo chmod 660 /run/gvmd/gvmd.sock
   ```

If doesn't work, try:

```bash
   sudo chmod 777 /run/gvmd/gvmd.sock
   ```

---

To run this:

```bash
   python3 gvm_agent.py
   ```