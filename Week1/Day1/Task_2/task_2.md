# HestaBit  
## Development Launchpad  
### Task 2  

**Submitted By:**  Aryan 
**Email:**  aryan@hestabit.in

---

## Install NVM

### 1. Download and Install NVM

**Terminal command:**
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/v0.40.3/install.sh | bash
```
![OS info](images/OSinfo.png)

**Description:** Downloads the official NVM installation script from the NVM GitHub repository and executes it to install Node Version Manager on the system.

---

### 2. Verification

**Terminal command:**
```bash
nvm -v
```
![OS info](images/OSinfo.png)

**Description:** Checks whether NVM has been installed successfully by displaying the currently installed NVM version.

---

## Switch Node from LTS -> Latest and back

### 1. Installing LTS version of Node.js

**Terminal command:**
```bash
nvm install --lts
```
![OS info](images/OSinfo.png)

**Description:** Downloads and installs the latest Long Term Support (LTS) version of Node.js using NVM.

---

### 2. Using LTS

**Terminal command:**
```bash
nvm use --lts
```
![OS info](images/OSinfo.png)

**Description:** Switches the active Node.js version to the installed LTS version for the current shell session.

