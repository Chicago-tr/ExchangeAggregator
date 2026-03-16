import { logLatency } from "./db/queries/latencies.js";

process.loadEnvFile();

//Can probably simplify these later since logic is very similar,
//maybe an exchange class and then turn each exchange into a subclass
//price = current ask

export class CoinbaseApi {
  private static readonly baseURL = "https://api.exchange.coinbase.com";

  private async fetchWithLatency(
    url: string,
  ): Promise<{ data: any; rttMs: number; statusCode: number; error?: string }> {
    const clientSendTs = Date.now();
    const perfStart = performance.now();

    try {
      const resp = await fetch(url, { method: "GET", mode: "cors" });
      const perfEnd = performance.now();
      const rttMs = perfEnd - perfStart;

      return {
        data: await resp.json(),
        rttMs,
        statusCode: resp.status,
        ...(resp.status >= 400 && {
          error: `${resp.status} ${resp.statusText}`,
        }),
      };
    } catch (error) {
      return {
        data: null,
        rttMs: performance.now() - perfStart,
        statusCode: 0,
        error: error instanceof Error ? error.message : "Network error",
      };
    }
  }
  //const pairs = envOrThrow("COINBASE_PAIRS")
  async fetchPrice(pair: string): Promise<BidAskData | null> {
    const url = `${CoinbaseApi.baseURL}/products/${pair}/ticker`;
    // const resp = await fetch(url, {
    //   method: "GET",
    //   mode: "cors",
    // });
    // if (!resp.ok) {
    //   throw new Error(`${resp.status} ${resp.statusText}`);
    // }
    const result = await this.fetchWithLatency(url);
    await logLatency({
      exchange: "coinbase",
      endpoint: new URL(url).pathname,
      symbol: pair,
      clientSendTs: Date.now() - Math.round(result.rttMs), // Approximate
      clientRecvTs: Date.now(),
      rttMs: result.rttMs,
      statusCode: result.statusCode,
      error: result.error,
    });
    if (!result.data || result.statusCode !== 200) {
      console.warn(`Coinbase ${pair} failed: ${result.statusCode}`);
      return null;
    }
    //const respJson: CoinbaseData = await resp.json();
    const bidNum = parseFloat(result.data.bid);
    const askNum = parseFloat(result.data.ask);

    const bidAsk = { bid: bidNum, ask: askNum };

    return bidAsk;
  }
}

export class BinanceApi {
  private static readonly baseURL =
    "https://api.binance.us/api/v3/ticker/bookTicker?symbol=";
  private async fetchWithLatency(
    url: string,
  ): Promise<{ data: any; rttMs: number; statusCode: number; error?: string }> {
    const clientSendTs = Date.now();
    const perfStart = performance.now();

    try {
      const resp = await fetch(url, { method: "GET", mode: "cors" });
      const perfEnd = performance.now();
      const rttMs = perfEnd - perfStart;

      return {
        data: await resp.json(),
        rttMs,
        statusCode: resp.status,
        ...(resp.status >= 400 && {
          error: `${resp.status} ${resp.statusText}`,
        }),
      };
    } catch (error) {
      return {
        data: null,
        rttMs: performance.now() - perfStart,
        statusCode: 0,
        error: error instanceof Error ? error.message : "Network error",
      };
    }
  }
  constructor() {}
  //const pairs = envOrThrow("BINANCE_PAIRS")

  async fetchPrice(pair: string): Promise<BidAskData | null> {
    const pre = pair.slice(0, 3);
    const suf = pair.slice(4);

    const newPair = pre + suf;

    const url = `${BinanceApi.baseURL}${newPair}`;
    const result = await this.fetchWithLatency(url);
    await logLatency({
      // Same structure
      exchange: "binance",
      endpoint: new URL(url).pathname,
      symbol: newPair,
      clientSendTs: Date.now() - Math.round(result.rttMs),
      clientRecvTs: Date.now(),
      rttMs: result.rttMs,
      statusCode: result.statusCode,
      error: result.error,
    });

    if (!result.data || result.statusCode !== 200) {
      console.warn(`Binance ${pair} failed: ${result.statusCode}`);
      return null;
    }

    // const resp = await fetch(url, {
    //   method: "GET",
    //   mode: "cors",
    // });
    // if (!resp.ok) {
    //   throw new Error(`${resp.status} ${resp.statusText}`);
    // }
    //const respJson: BinanceData = await resp.json();

    let roundedBid = Number(parseFloat(result.data.bidPrice).toFixed(2));
    const roundedAsk = Number(parseFloat(result.data.askPrice).toFixed(2));

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
