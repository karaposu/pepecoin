
# Troubleshooting Guide

No worries, we are all pessimists, so no error can scare us anyway.

Let’s first figure out what is working and what isn’t.

Our goal is to get the `pepecoin-cli getblockchaininfo` command to output a JSON response.

### Step 1: Check if `pepecoind` is running

Run the following command:

```bash
ps aux | grep pepecoind
```

- If this does not produce any output, it means the installation was problematic, and you should reinstall it.
- If there is output, that’s a good sign—move to the next step.

### Step 2: Verify the configuration file

Check the contents of the configuration file to ensure your RPC credentials and port are correct:

```bash
cat "$HOME/Library/Application Support/Pepecoin/pepecoin.conf"
```

- Confirm that the RPC credentials are correct and that the port is set to `33873`.

### Step 3: Test the RPC command

Run the following command, replacing `your_rpc_username` and `your_rpc_password` with your actual RPC credentials:

```bash
curl --user your_rpc_username:your_rpc_password --data-binary '{"jsonrpc":"1.0","id":"curltest","method":"getblockchaininfo","params":[]}' -H 'content-type:text/plain;' http://127.0.0.1:33873/
```

- Observe the output to see if it contains useful information.

### Step 4: Check the logs (for MacOS)

Inspect the logs for any errors:

```bash
tail -n 50 "$HOME/Library/Application Support/Pepecoin/debug.log"
```

- These logs are valuable for diagnosing issues. Look for any errors in the output.

### Step 5: Reindex the chain state

If the logs show confusing errors, follow these steps:

1. Stop the Pepecoin daemon:
   ```bash
   pepecoin-cli stop
   ```

2. Reindex the chain state:
   ```bash
   pepecoind -daemon -reindex-chainstate
   ```
   note that this can take some time like an hour.

3. Check the logs again to ensure progress is being made:
   ```bash
   tail -n 50 "$HOME/Library/Application Support/Pepecoin/debug.log"
   ```

- Wait until you see `progress=1.000000` in the logs.

### Step 6: Test the JSON output again

Finally, run the following command once more to confirm the JSON output:

```bash
pepecoin-cli getblockchaininfo
```

If everything is configured correctly, you should see the expected JSON response.

--- 



