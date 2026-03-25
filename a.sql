SELECT COUNT(*) FROM (

SELECT  actor_name, COUNT(b.fr_id) as cnt FROM (
    SELECT fr_id, fr_actor FROM 
(
        SELECT page_title FROM categorylinks JOIN page 
    ON cl_from = page_id
    WHERE cl_target_id = (
        SELECT lt_id FROM linktarget WHERE 
        lt_namespace=14 AND lt_title='Images_from_Wiki_Loves_Folklore_2026'
    )
) AS a JOIN file JOIN filerevision ON a.page_title = file_name 
AND fr_id = file_latest
) AS b LEFT JOIN actor ON b.fr_actor = actor_id
GROUP BY actor_id ORDER BY cnt DESC

) as s;


SELECT COUNT(*) FROM (
    SELECT actor_name, COUNT(fr_id) AS cnt
    FROM linktarget
    JOIN categorylinks ON lt_id = cl_target_id
    JOIN page ON cl_from = page_id
    JOIN file ON page_title = file_name
    JOIN filerevision ON fr_id = file_latest
    JOIN actor ON fr_actor = actor_id
    WHERE lt_namespace = 14 
      AND lt_title = 'Images_from_Wiki_Loves_Folklore_2026'
    GROUP BY actor_id
) AS s;

select SUM(cnt) from (select actor_name, count( distinct a.fr_id) as
cnt from (select distinct fr_id, fr_actor from categorylinks join page join file join filerevi
sion  on  fr_id = file_latest and file_name=page_title and  cl_from=page_id where cl_target_id
=(select lt_id from linktarget where lt_namespace=14 and lt_title='Images_from_Wiki_Loves_Folk
lore_2026')) as a left join actor on a.fr_actor = actor_id group by actor_id) as s;