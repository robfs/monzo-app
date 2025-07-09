CREATE OR REPLACE TABLE paydays AS
WITH month_series AS (
    SELECT
        date_part('year', date_series) as year,
        date_part('month', date_series) as monthNum
    FROM generate_series(
        DATE '2017-01-01',
        DATE '2030-12-01',
        INTERVAL '1 month'
    ) as t(date_series)
)
    SELECT
        year,
        monthNum,
        make_date(
            CAST(year AS INTEGER),
            CAST(monthNum AS INTEGER),
            ?
        ) + INTERVAL (
            CASE
                WHEN date_part('isodow', make_date(CAST(year AS INTEGER), CAST(monthNum AS INTEGER), 25)) BETWEEN 1 AND 5 THEN 0
                WHEN date_part('isodow', make_date(CAST(year AS INTEGER), CAST(monthNum AS INTEGER), 25)) = 6 THEN 2  -- Saturday -> Monday
                WHEN date_part('isodow', make_date(CAST(year AS INTEGER), CAST(monthNum AS INTEGER), 25)) = 7 THEN 1  -- Sunday -> Monday
            END
        ) DAY as lastDate,
        lead(lastDate) over (order by lastDate) as nextDate
    FROM month_series
ORDER BY year, monthNum
