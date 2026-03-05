CREATE TABLE "etl_state" (
	"id" varchar PRIMARY KEY NOT NULL,
	"Timestamp" timestamp DEFAULT now() NOT NULL
);
