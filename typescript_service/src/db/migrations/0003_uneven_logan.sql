ALTER TABLE "exchanges" RENAME COLUMN "ExchangeName" TO "exchange_name";--> statement-breakpoint
ALTER TABLE "prices" RENAME COLUMN "TimeStamp" TO "timestamp";--> statement-breakpoint
ALTER TABLE "prices" RENAME COLUMN "Bid" TO "bid";--> statement-breakpoint
ALTER TABLE "prices" RENAME COLUMN "Ask" TO "ask";--> statement-breakpoint
ALTER TABLE "prices" RENAME COLUMN "ExchangeId" TO "exchange_id";--> statement-breakpoint
ALTER TABLE "prices" RENAME COLUMN "SymbolId" TO "symbol_id";--> statement-breakpoint
ALTER TABLE "symbols" RENAME COLUMN "BaseAsset" TO "base_asset";--> statement-breakpoint
ALTER TABLE "symbols" RENAME COLUMN "QuoteAsset" TO "quote_asset";--> statement-breakpoint
ALTER TABLE "symbols" RENAME COLUMN "SymbolCode" TO "symbol_code";--> statement-breakpoint
ALTER TABLE "exchanges" DROP CONSTRAINT "exchanges_ExchangeName_unique";--> statement-breakpoint
ALTER TABLE "symbols" DROP CONSTRAINT "symbols_BaseAsset_QuoteAsset_SymbolCode_unique";--> statement-breakpoint
ALTER TABLE "prices" DROP CONSTRAINT "prices_ExchangeId_exchanges_id_fk";
--> statement-breakpoint
ALTER TABLE "prices" DROP CONSTRAINT "prices_SymbolId_symbols_id_fk";
--> statement-breakpoint
ALTER TABLE "prices" ADD CONSTRAINT "prices_exchange_id_exchanges_id_fk" FOREIGN KEY ("exchange_id") REFERENCES "public"."exchanges"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "prices" ADD CONSTRAINT "prices_symbol_id_symbols_id_fk" FOREIGN KEY ("symbol_id") REFERENCES "public"."symbols"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "exchanges" ADD CONSTRAINT "exchanges_exchange_name_unique" UNIQUE("exchange_name");--> statement-breakpoint
ALTER TABLE "symbols" ADD CONSTRAINT "symbols_base_asset_quote_asset_symbol_code_unique" UNIQUE("base_asset","quote_asset","symbol_code");