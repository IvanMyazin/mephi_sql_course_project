-- 1
SELECT *
FROM taxi.vehicles
WHERE registration_number ~ '(77|97|99|177|197|199|777|797|799|977|997)$';

-- 2
SELECT v.registration_number, COUNT(o.id) AS orders_count
FROM taxi.vehicles v
JOIN taxi.drivers d ON d.vehicle_id = v.id
JOIN taxi.orders o ON o.driver_id = d.id
GROUP BY v.registration_number;
