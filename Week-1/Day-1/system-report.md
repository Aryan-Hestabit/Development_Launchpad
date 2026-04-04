# HestaBit  
## Development Launchpad  
### Task 1  

**Submitted By:** Aryan

**Email:** aryan@hestabit.in  

---

## Identify and document

### 1. OS version
**Terminal command:**
```bash
lsb_release -a
```
![OS info](images/OSinfo.png)

**Description:** Displays detailed information about the Linux distribution currently installed on the system, including distributor ID, description, release number, and codename.

---

### 2. Current Shell
**Terminal command:**
```bash
echo $SHELL
```
![Shell](images/Shell.png)

**Description:** Prints the path of the default shell that is currently being used by the user (for example, bash or zsh).

---

### 3. Node binary path
**Terminal command:**
```bash
which node
```
![nodePath](images/nodePath.png)

**Description:** Shows the exact file system location of the Node.js executable that is being used when the `node` command is run.

---

### 4. NPM global installation path
**Terminal command:**
```bash
npm config get prefix
```
![npmPath](images/npmPath.png)

**Description:** Displays the directory where npm installs global packages and binaries by default.

---

### 5. PATH Entries with “node” or “npm”
**Terminal command:**
```bash
echo $PATH | grep -i 'node\|npm'
```
![PathEntries](images/PathEntries.png)

**Description:** Filters and displays only those entries from the system PATH environment variable that contain the words "node" or "npm", helping identify relevant executable paths.

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
![nvmInstall](images/nvmInstall.png)

**Description:** Downloads the official nvm installation script from the nvm GitHub repository and executes it to install Node Version Manager on the system.

---

### 2. Verification

**Terminal command:**
```bash
nvm -v
```
![nvmVersion](images/nvmVersion.png)

**Description:** Verifies the installation of nvm in the kernel by displaying it's version.

---

## Switch Node from LTS -> Latest and back

### 1. Installing LTS version of Node.js

**Terminal command:**
```bash
nvm install --lts
```
![ltsInstall](images/ltsInstall.png)

**Description:** Downloads and installs the latest Long Term Support (LTS) version of Node.js using nvm.

---

### 2. Using LTS

**Terminal command:**
```bash
nvm use --lts
```
![uselts](images/uselts.png)

**Description:** Switches the active Node.js version to the installed LTS version for the current shell session.

