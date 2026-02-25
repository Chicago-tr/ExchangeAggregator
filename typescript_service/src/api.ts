process.loadEnvFile();

//Can probably simplify these later since logic is very similar

export class CoinbaseApi {
  private static readonly baseURL = "https://api.exchange.coinbase.com";
  //const pairs = envOrThrow("COINBASE_PAIRS")
  async fetchPrice(pair: string) {
    const url = `${CoinbaseApi.baseURL}/products/${pair}/ticker`;
    const resp = await fetch(url, {
      method: "GET",
      mode: "cors",
    });
    if (!resp.ok) {
      throw new Error(`${resp.status} ${resp.statusText}`);
    }
    const respJson: CoinbaseData = await resp.json();
    const price = respJson.price;

    return Number(price);
  }
}

export class BinanceApi {
  private static readonly baseURL =
    "https://api.binance.us/api/v3/ticker/price?symbol=";

  constructor() {}
  //const pairs = envOrThrow("BINANCE_PAIRS")

  async fetchPrice(pair: string) {
    const url = `${BinanceApi.baseURL}${pair}`;

    const resp = await fetch(url, {
      method: "GET",
      mode: "cors",
    });
    if (!resp.ok) {
      throw new Error(`${resp.status} ${resp.statusText}`);
    }
    const respJson: BinanceData = await resp.json();

    const price = respJson.price;
    const rounded = parseFloat(price).toFixed(2);

    return Number(rounded);
  }
}

export type BinanceData = {
  symbol: string;
  price: string;
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
