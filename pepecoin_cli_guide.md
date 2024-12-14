# Here i will share some common commands. 

## get address' account 

``` pepecoin-cli getaccount "PY7gSQ9w28F7t7BK5AWyvKi1vsjw31uUQv" ```


## get received amount in address 

pepecoin-cli getreceivedbyaddress "PdUKs4Ko1nkgX5vk81pGisA7LNNyFjvAJk"
pepecoin-cli getreceivedbyaddress "PqsvAyU1GBnWj1Aa9g3EfgtYnXD87MDjA5"


## get balance  in address 
pepecoin-cli getbalance "source_account"


## list all accounts 

pepecoin-cli listaccounts



## get addresses by account 

``` pepecoin-cli getaddressesbyaccount "destination_account" ```
``` pepecoin-cli getaddressesbyaccount "source_account" ```


## unlock wallet 

pepecoin-cli walletpassphrase "your_wallet_password" 600


## send pepecoin  (Account-Based)

pepecoin-cli sendfrom "source_account" "destination_address" amount "comment" "comment_to"

pepecoin-cli sendfrom "source_account" "PY7gSQ9w28F7t7BK5AWyvKi1vsjw31uUQv" 0.5 "Test transfer" "Test transfer to destination"


## send pepecoin  (Address-Based-Based)

pepecoin-cli sendtoaddress "destination_address" amount "comment" "comment_to"

pepecoin-cli sendtoaddress "PY7gSQ9w28F7t7BK5AWyvKi1vsjw31uUQv" 0.5 "Test transfer" "Test transfer to destination"


## watch transaction status 

pepecoin-cli gettransaction "transaction_id"

## list recent transactions 

pepecoin-cli listtransactions

<!-- ## Verify Address Ownership

pepecoin-cli getaddressinfo "PdUKs4Ko1nkgX5vk81pGisA7LNNyFjvAJk" -->









 pepecoin-cli listaccounts