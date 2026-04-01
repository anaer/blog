```sql
CREATE DEFINER=`root`@`%` PROCEDURE `DeleteChildren`(IN rootId INT)
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE childId INT;
    -- 定义游标遍历所有子节点
    DECLARE cur CURSOR FOR SELECT id FROM system_menu WHERE parent_id = rootId;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO childId;
        IF done THEN
            LEAVE read_loop;
        END IF;
        -- 递归调用自身删除子节点的子节点
        CALL DeleteChildren(childId);
        -- 删除当前子节点
        DELETE FROM system_menu WHERE id = childId;
	DELETE FROM system_role_menu WHERE menu_id = childId;
    END LOOP;
    CLOSE cur;
END
```

```sql
SET SESSION max_sp_recursion_depth = 255; 
CALL DeleteChildren(4000);
SET SESSION max_sp_recursion_depth = 0; 
```

`SET SESSION max_sp_recursion_depth = 255; ` 解决以下报错
Recursive limit 0 (as set by the max_sp_recursion_depth variable) was exceeded for routine DeleteChildren