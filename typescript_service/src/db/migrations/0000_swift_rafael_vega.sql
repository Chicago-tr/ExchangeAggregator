CREATE TABLE "exchanges" (
	"id" serial PRIMARY KEY NOT NULL,
	"ExchangeName" varchar,
	CONSTRAINT "exchanges_ExchangeName_unique" UNIQUE("ExchangeName")
);
--> statement-breakpoint
CREATE TABLE "prices" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"TimeStamp" timestamp DEFAULT now() NOT NULL,
	"Bid" real,
	"Ask" real,
	"ExchangeId" integer,
	"SymbolId" integer
);
--> statement-breakpoint
CREATE TABLE "symbols" (
	"id" serial PRIMARY KEY NOT NULL,
	"BaseAsset" varchar,
	"QuoteAsset" varchar,
	"SymbolCode" varchar,
	CONSTRAINT "symbols_BaseAsset_QuoteAsset_SymbolCode_unique" UNIQUE("BaseAsset","QuoteAsset","SymbolCode")
);
--> statement-breakpoint
ALTER TABLE "prices" ADD CONSTRAINT "prices_ExchangeId_exchanges_id_fk" FOREIGN KEY ("ExchangeId") REFERENCES "public"."exchanges"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "prices" ADD CONSTRAINT "prices_SymbolId_symbols_id_fk" FOREIGN KEY ("SymbolId") REFERENCES "public"."symbols"("id") ON DELETE no action ON UPDATE no action;