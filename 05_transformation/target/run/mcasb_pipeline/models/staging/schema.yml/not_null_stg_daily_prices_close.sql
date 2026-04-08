
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select close
from `warehouse`.`stg_daily_prices`
where close is null



  
  
    ) dbt_internal_test