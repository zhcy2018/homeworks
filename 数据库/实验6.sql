/*
BEGIN TRAN TEST123
	INSERT INTO C VALUES('C01022','TEST',NULL,1);
	INSERT INTO C VALUES('C01023','TEST',NULL,1);
select   *   from fn_dblog(null,null) 
DBCC log (SM)
*/
/*
backup database SM to disk = 'C:\Users\zcy\Desktop\tmp\1.db'
with noinit;-- WITH DIFFERENTIAL 
restore database SM FROM disk = 'C:\Users\zcy\Desktop\tmp\1.db'
with RECOVERY
*/
/*
use master
backup database SM to disk = 'C:\Users\zcy\Desktop\tmp\1.db'
with  DIFFERENTIAL ;
declare @dbname varchar(20)
set @dbname='SM'

declare @sql nvarchar(500)
declare @spid int--SPID 值是当用户进行连接时指派给该连接的一个唯一的整数
set @sql='declare getspid cursor for
select spid from sysprocesses where dbid=db_id('''+@dbname+''')'
exec (@sql)
open getspid
fetch next from getspid into @spid
while @@fetch_status<>-1--如果FETCH 语句没有执行失败或此行不在结果集中。
begin
exec('kill '+@spid)--终止正常连接
fetch next from getspid into @spid
end
close getspid
deallocate getspid
restore database SM FROM disk = 'C:\Users\zcy\Desktop\tmp\1.db'
with REPLACE
*/