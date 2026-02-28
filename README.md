# Cyber Security Threat & Insurance Analysis 2025

An analysis of the 2025 cyber threat landscape drawing on three major industry reports:
**IBM Cost of a Data Breach**, **Verizon DBIR**, and the **NAIC Cybersecurity Insurance Market Report**.

[![Open IBM Analysis in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://githubtocolab.com/cvanstey/cyber_security_analysis/blob/main/IBMEDA.py)
[![Open Verizon Analysis in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://githubtocolab.com/cvanstey/cyber_security_analysis/blob/main/verizon.py)
[![Open NAIC Analysis in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://githubtocolab.com/cvanstey/cyber_security_analysis/blob/main/NAICS.py)

---

## Key Findings

### The threat landscape is consolidating around a few dominant patterns
System Intrusion is the top breach pattern (Verizon), driven almost entirely by Malware (54% of all breaches). Phishing is the most frequent initial access vector (IBM, 16%) but Supply Chain Compromise is close behind at 15% and actually costs more per breach ($4.91M vs $4.80M). These aren't separate problems — phishing gets credentials, malware executes, supply chain amplifies the blast radius. One attack, three statistics.

### The human element remains the core vulnerability
60% of breaches involve a human element (Verizon/NAIC). Phishing, stolen credentials, and insider error account for 40% of IBM's attack vectors combined. The +800% rise in stolen credentials in H1 2025 (NAIC) and the +442% surge in vishing suggest attackers are accelerating their investment in social engineering faster than defenders are responding.

### The financial exposure is heavily concentrated
The US pays a massive premium — $10.22M average vs $4.44M globally. The top 3 countries represent 35.7% of all breach costs. In the insurance market, the top 5 insurers hold the majority of market share, and the top 5 states account for 64.5% of premiums. Risk is not evenly distributed — it clusters around large, regulated, English-speaking economies.

### AI is the clearest lever available
Extensive AI adoption cuts breach cost by $1.90M (34.4%) and reduces detection and containment time by 80 days. DevSecOps is the single biggest cost reducer. Meanwhile, Shadow AI adds $200K to breach costs and 63% of organisations have no AI governance. The gap between organisations using AI defensively and those creating new attack surface through ungoverned AI adoption is widening fast.

### The insurance market is feeling the squeeze
The US market declined 7.1% in 2024 while claims rose ~40%. Loss ratios are rising — several of the top 20 insurers are above 75%. Ransomware is in 44% of breaches but 64% of victims are now refusing to pay and average ransom payments dropped 77%. That's good for victims but it means attackers are pivoting to data extortion and business disruption instead, which is harder to price.

### The single most important implication
The organisations most at risk are large, US-based, with complex supply chains, limited AI security tooling, and no AI governance policy. That profile describes a lot of financial services, healthcare, and technology companies — which is exactly why those three industries dominate the top of both the IBM cost rankings and the NAIC premium concentration data. The threat is not random. It's targeted, automated, and getting cheaper to execute while getting more expensive to recover from.

---

## Running the Analysis

### Option 1 — Google Colab (no setup required)
Click any badge above. Then run this in the first cell:

```python
!git clone https://github.com/cvanstey/cyber_security_analysis
%cd cyber_security_analysis
!pip install openpyxl scikit-learn -q
```

Then run the script:
```python
%run IBMEDA.py      # IBM Cost of a Data Breach
%run verizon.py     # Verizon DBIR
%run NAICS.py       # NAIC Insurance Market
```

### Option 2 — Local
```bash
git clone https://github.com/cvanstey/cyber_security_analysis
cd cyber_security_analysis
pip install pandas numpy matplotlib openpyxl scikit-learn
python IBMEDA.py
python verizon.py
python NAICS.py
```

---

## Data Sources
| Report | Publisher | Year |
|---|---|---|
| Cost of a Data Breach Report | IBM / Ponemon Institute | 2025 |
| Data Breach Investigations Report (DBIR) | Verizon | 2025 |
| Cybersecurity Insurance Market Report | NAIC | 2025 |

---

## Requirements
- Python 3.9+
- pandas, numpy, matplotlib, openpyxl, scikit-learn
