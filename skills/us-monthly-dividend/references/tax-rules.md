# US Dividend Taxation for Korean Residents

General rules for dividends from US-listed stocks/ETFs held by a Korean tax
resident through a Korean brokerage. Rates change — when the user needs
precision (large amounts, filing) verify the current law with a web search
before answering.

## Withholding chain

1. **US withholding: 15%** under the KR-US tax treaty (Korean brokers file
   W-8BEN automatically). Applied at source before the dividend lands.
2. **Korean withholding: none in the common case.** Korea's dividend income
   tax is 14% (+1.4% local surtax). Because the US already withheld 15% ≥ 14%,
   Korean brokers withhold nothing further on US dividends.
   - Counter-case: dividends from a country withholding under 14% get the
     difference withheld in Korea. Does not apply to US holdings.

**Default after-tax formula: `net = gross × 0.85`.**

## 금융소득종합과세 (comprehensive financial income taxation)

- Trigger: total annual financial income (interest + dividends, worldwide,
  gross) **over 20,000,000 KRW**.
- Effect: the excess joins global income and is taxed at progressive rates
  (6.6%–49.5% including local surtax), with a foreign tax credit for the 15%
  already withheld in the US.
- The skill does not compute this liability — it only flags when the
  portfolio's projected annual gross dividends exceed the threshold and tells
  the user to consult the numbers with a tax professional.

## Account-type notes

- Figures above assume a regular taxable brokerage account (일반계좌).
- 연금저축/IRP/ISA accounts cannot hold US-listed stocks directly (only
  Korean-listed ETFs), so they are out of scope for this skill's US-ticker
  calculations. If the user asks about them, say so instead of adapting the
  formula.
