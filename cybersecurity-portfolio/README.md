
# Malware Analysis Report – C2 Infrastructure

## Overview
This repository contains a **comprehensive malware analysis report** investigating a phishing campaign and its associated **Command and Control (C2) infrastructure**. The report includes findings on **malicious domains, IP addresses, SSL certificates, and passive DNS data**, as well as **recommendations for threat mitigation**.

## Contents
- `malware_analysis_report.pdf` – The detailed investigation report.  
- `README.md` – This document, providing an overview of the report.  
- `ioc_blocklist.txt` – A plain text file listing **all malicious domains and IPs** for easy security implementation.  
- `raw_dns_findings.csv` – A dataset of passive DNS resolutions from WhoisXMLAPI.  
- `related_threats_notes.md` – Additional research findings on connected malware threats.

## Key Findings
- **18 malicious IPs** identified, linked to phishing, data exfiltration, and malware activity.
- **15 malicious domains** confirmed as part of an evolving cyber threat campaign.
- **Suspicious SSL certificate** for `github.com` found linked to infrastructure abuse.
- **Historical passive DNS** shows repeated domain shifts to evade detection.

## How to Use This Report
Security analysts and **SOC teams** can use this repository to:
1. **Blacklist identified malicious IPs and domains** to prevent future attacks.
2. **Monitor outbound traffic** for signs of Command and Control (C2) activity.
3. **Correlate findings with active threat intelligence** to expand investigations.
4. **Enhance phishing awareness and response measures** based on observed tactics.

## Further Investigation
To expand upon these findings, analysts can:
- Conduct additional **passive DNS lookups** for newly discovered domains.
- Perform **deep SSL certificate analysis** using `crt.sh` and `Censys.io`.


## Contributors
This analysis was conducted by:
- **Nelson**


## License
This report and associated files are released under the **MIT License** for security research and educational use.

---

## Contact
For questions or further inquiries, please reach out via GitHub Issues or direct email.

---

