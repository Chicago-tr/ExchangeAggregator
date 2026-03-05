process.loadEnvFile();

//Can probably simplify these later since logic is very similar
//price = current ask

export class CoinbaseApi {
  private static readonly baseURL = "https://api.exchange.coinbase.com";
  //const pairs = envOrThrow("COINBASE_PAIRS")
  async fetchPrice(pair: string): Promise<BidAskData> {
    const url = `${CoinbaseApi.baseURL}/products/${pair}/ticker`;
    const resp = await fetch(url, {
      method: "GET",
      mode: "cors",
    });
    if (!resp.ok) {
      throw new Error(`${resp.status} ${resp.statusText}`);
    }
    const respJson: CoinbaseData = await resp.json();
    const bidNum = parseFloat(respJson.bid);
    const askNum = parseFloat(respJson.ask);

    const bidAsk = { bid: bidNum, ask: askNum };

    return bidAsk;
  }
}

export class BinanceApi {
  private static readonly baseURL =
    "https://api.binance.us/api/v3/ticker/bookTicker?symbol=";

  constructor() {}
  //const pairs = envOrThrow("BINANCE_PAIRS")

  async fetchPrice(pair: string): Promise<BidAskData> {
    const pre = pair.slice(0, 3);
    const suf = pair.slice(4);

    const newPair = pre + suf;

    const url = `${BinanceApi.baseURL}${newPair}`;

    const resp = await fetch(url, {
      method: "GET",
      mode: "cors",
    });
    if (!resp.ok) {
      throw new Error(`${resp.status} ${resp.statusText}`);
    }
    const respJson: BinanceData = await resp.json();

    let roundedBid = Number(parseFloat(respJson.bidPrice).toFixed(2));
    const roundedAsk = Number(parseFloat(respJson.askPrice).toFixed(2));

    const bidAsk = { bid: roundedBid, ask: roundedAsk };

    return bidAsk;
  }
}
export type BidAskData = {
  bid: number;
  ask: number;
};

export type BinanceData = {
  symbol: string;
  bidPrice: string;
  bidQty: string;
  askPrice: string;
  askQty: string;
};

export type CoinbaseData = {
  ask: string;
  bid: string;
  volume: string;
  trade_id: number;
  price: string;
  size: string;
  time: string;
  rfq_volume: string;
};
