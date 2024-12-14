
### **How to Check if Pepecoin Core is Already Running**

#### **1. Use `pepecoin-cli` to Interact with the Running Node**

Since Pepecoin Core is likely running, you can use `pepecoin-cli` to check its status.

**Command:**

```bash
pepecoin-cli getblockchaininfo
```

**Expected Output:**

If the node is running and your RPC credentials are correct, you'll receive detailed blockchain information, such as:

```
{
  "chain": "main",
  "blocks": 123456,
  "headers": 123456,
  "bestblockhash": "0000000000000abcdef...",
  "difficulty": 1234567.890123,
  "verificationprogress": 0.987654321,
  "initialblockdownload": false,
  
}
```

#### **. if `pepecoin-cli` not found** 
This means it is not added to the PATH.  First we should locate it via 

```find / -name pepecoin-cli 2>/dev/null```

If there is a result then we should can add it to path via (dont forget to replace the /path/to/pepecoin-cli part )

``` export PATH="/path/to/pepecoin-cli:$PATH" ```


**If you receive an error:**

- **Error Message:**

  ```
  error: Could not connect to the server 127.0.0.1:33873 (error code 1 - "EOF reached")
  Make sure the pepecoind server is running and that you are connecting to the correct RPC port.
  ```

- **Possible Causes:**
  - The Pepecoin daemon is not running.
  - RPC credentials in `pepecoin.conf` are incorrect.

#### **2. Check for Running `pepecoind` Process**

You can verify if `pepecoind` is running by checking the running processes.

**Command:**

```bash
ps aux | grep pepecoind | grep -v grep
```

**Explanation:**

- `ps aux`: Lists all running processes.
- `grep pepecoind`: Filters for `pepecoind`.
- `grep -v grep`: Excludes the `grep` command itself from the results.

**Example Output:**

```
enes     12345  0.1  1.0 123456 7890 ?        Ssl  10:00   0:05 pepecoind -daemon
```

If you see a line like this, it means `pepecoind` is running.

#### **3. Check Open Ports with `lsof`**

Verify if the default RPC port (`33873`) is in use.

**Command:**

```bash
lsof -i :33873
```

**Example Output:**

```
COMMAND    PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
pepecoind 12345 enes   10u  IPv4 123456      0t0  TCP localhost:33873 (LISTEN)
```

This indicates that `pepecoind` is listening on port `33873`.

---

### **What to Do Next**

#### **If Pepecoin Core Is Running**

Since the node is already running, you can start using `pepecoin-cli` to interact with it.

**Try Running:**

```bash
pepecoin-cli getnetworkinfo
```

**Note:** Ensure that your `pepecoin.conf` file has the correct `rpcuser` and `rpcpassword`. The `pepecoin-cli` uses these credentials to communicate with the daemon.

#### **If You Need to Stop Pepecoin Core**

If you want to stop the running `pepecoind` instance:

**Command:**

```bash
pepecoin-cli stop
```

This will gracefully shut down the Pepecoin daemon.

#### **If You Believe Pepecoin Core Is Not Running**

If you suspect that the daemon is not running but you still receive the lock error, it might be due to a stale lock file.

##### **Check for Stale Lock File**

**Command:**

```bash
ls -la ~/.pepecoin/.lock
```

- If the `.lock` file exists but `pepecoind` is not running, it might be preventing the daemon from starting.
- **Remove the Lock File:**

  ```bash
  rm ~/.pepecoin/.lock
  ```

**Caution:** Only remove the lock file if you're certain that `pepecoind` is not running.

---

### **Additional Troubleshooting Steps**

#### **1. Verify RPC Credentials**

Ensure that the `rpcuser` and `rpcpassword` in your `pepecoin.conf` match those you're using with `pepecoin-cli`.

**View `pepecoin.conf`:**

```bash
cat ~/.pepecoin/pepecoin.conf
```

#### **2. Restart the Pepecoin Daemon**

If you stopped the daemon or after removing a stale lock file, you can start it again:

```bash
pepecoind -daemon
```

#### **3. Check the Pepecoin Debug Log**

Inspect the `debug.log` file for any error messages.

**Command:**

```bash
tail -f ~/.pepecoin/debug.log
```

Look for any errors or warnings that might indicate why the daemon couldn't start or if it exited unexpectedly.

---


### **Example Commands**

**Check if Pepecoin Core is Running:**

```bash
pepecoin-cli getblockchaininfo
```

**Check for `pepecoind` Process:**

```bash
ps aux | grep pepecoind | grep -v grep
```

**Stop Pepecoin Core:**

```bash
pepecoin-cli stop
```

**Start Pepecoin Core:**

```bash
pepecoind -daemon
```

**View Debug Log:**

```bash
tail -f ~/.pepecoin/debug.log
```

