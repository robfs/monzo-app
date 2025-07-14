ALTER VIEW transactions RENAME TO RAW_TRANSACTIONS;

CREATE OR REPLACE TABLE transactions
AS SELECT
    raw_transactions.*,
    paydays.*,
    if (raw_transactions.date < paydays.lastDate, paydays.lastDate, paydays.nextDate) as nextPayDay,
    date_trunc('month', nextPayDay) as expenseMonthDate,
    case date_part('month', expenseMonthDate)
        when 1 then 'January'
        when 2 then 'February'
        when 3 then 'March'
        when 4 then 'April'
        when 5 then 'May'
        when 6 then 'June'
        when 7 then 'July'
        when 8 then 'August'
        when 9 then 'September'
        when 10 then 'October'
        when 11 then 'November'
        when 12 then 'December'
    end || ' ' || date_part('year', expenseMonthDate) as expenseMonth,
    date_part('isodow', date) as dayOfWeekNum,
    case dayOfWeekNum
        when 1 then 'Monday'
        when 2 then 'Tuesday'
        when 3 then 'Wednesday'
        when 4 then 'Thursday'
        when 5 then 'Friday'
        when 6 then 'Saturday'
        when 7 then 'Sunday'
    end as dayOfWeek,
    case monthNum
        when 1 then 'January'
        when 2 then 'February'
        when 3 then 'March'
        when 4 then 'April'
        when 5 then 'May'
        when 6 then 'June'
        when 7 then 'July'
        when 8 then 'August'
        when 9 then 'September'
        when 10 then 'October'
        when 11 then 'November'
        when 12 then 'December'
    end as month,
    sum(amount) OVER (ORDER BY date, time ROWS UNBOUNDED PRECEDING) as balance
FROM raw_transactions
LEFT JOIN paydays ON date_part('year', raw_transactions.date) = paydays.year AND date_part('month', raw_transactions.date) = paydays.monthNum;
