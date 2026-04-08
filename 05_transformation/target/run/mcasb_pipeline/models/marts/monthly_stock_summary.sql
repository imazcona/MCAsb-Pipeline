

  create or replace view `warehouse`.`monthly_stock_summary` 
  
    
  
  
    
    
  as (
    SELECT
    ticker,
    toStartOfMonth(date) AS month,
    round(avg(open), 2) AS avg_open_price,
    round(avg(close), 2) AS avg_close_price,
    round((avg(open) + avg(close)) / 2, 2) AS avg_price,
    round(avg(volume), 0) AS avg_volume,
    count(*) AS trading_days
FROM `warehouse`.`stg_daily_prices`
GROUP BY ticker, toStartOfMonth(date)
ORDER BY ticker, month
    
  )
      
      
                    -- end_of_sql
                    
                    