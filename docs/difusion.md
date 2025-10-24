```mermaid
graph LR
  Broadcast[Broadcast: Top 5 Criptos]
  MulticastBTC[Multicast: Bitcoin]
  MulticastETH[Multicast: Ethereum]
  MulticastUSDT[Multicast: USDT]
  MulticastBNB[Multicast: BNB]
  MulticastSOL[Multicast: Solana]

  IndexPage[Cliente en index]
  BTCPage[Cliente en /bitcoin]
  ETHPage[Cliente en /eth]
  USDTPage[Cliente en /usdt]
  BNBPage[Cliente en /bnb]
  SOLPage[Cliente en /sol]

  Broadcast --> IndexPage
  Broadcast --> BTCPage
  Broadcast --> ETHPage
  Broadcast --> USDTPage
  Broadcast --> BNBPage
  Broadcast --> SOLPage

  MulticastBTC --> BTCPage
  MulticastETH --> ETHPage
  MulticastUSDT --> USDTPage
  MulticastBNB --> BNBPage
  MulticastSOL --> SOLPage
```