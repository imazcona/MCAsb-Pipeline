

  create or replace view `warehouse`.`stg_daily_prices` 
  
    
  
  
    
    
  as (
    SELECT
    ticker,
    date,
    open,
    high,
    low,
    close,
    volume
FROM `warehouse`.`daily_prices`
WHERE close > 0 AND volume > 0
    
  )
      
      
                    -- end_of_sql
                    
                    