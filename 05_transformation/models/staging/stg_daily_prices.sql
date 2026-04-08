SELECT
    ticker,
    date,
    open,
    high,
    low,
    close,
    volume
FROM {{ source('warehouse', 'daily_prices') }}
WHERE close > 0 AND volume > 0
