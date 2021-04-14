/*
-- 仅含有创建部分代码，测试要自己写
CREATE LOGIN dlm1 
    WITH PASSWORD = '12345678', DEFAULT_DATABASE = SM;
CREATE USER U1 FOR LOGIN dlm1;
CREATE LOGIN dlm2 
    WITH PASSWORD = '12345678', DEFAULT_DATABASE = SM;
CREATE USER U2 FOR LOGIN dlm2;
CREATE LOGIN dlm3
    WITH PASSWORD = '12345678', DEFAULT_DATABASE = SM;
CREATE USER U3 FOR LOGIN dlm3;
CREATE LOGIN dlm4 
    WITH PASSWORD = '12345678', DEFAULT_DATABASE = SM;
CREATE USER U4 FOR LOGIN dlm4;
CREATE LOGIN dlm5 
    WITH PASSWORD = '12345678', DEFAULT_DATABASE = SM;
CREATE USER U5 FOR LOGIN dlm5;
*/
--exec sp_helpuser;
--GRANT ALL ON S TO U1 --WITH GRANT OPTION
/*
grant all privileges
on S
to u2,u3;
grant all privileges
on C
to u2,u3;
*/
/*
grant select
on sc
to public;
*/
/*
grant select,update(sname)
on S
to U4;
*/
/*
grant insert
on SC
to U1
with grant option;
*/



/*
revoke select
on sc
from public;
*/
/*
revoke INSERT
on SC
from U5;  -- 这个我没有测试成功，还是能正常insert，现在原因未知
*/


--EXEC sp_addlogin 'test', 'test', 'SM'
--exec sp_droplogin 'test'
--exec sp_addrole 'test1'
--exec sp_adduser 'test','SM'

--exec sp_helplogins
--exec sp_defaultdb 'test','SM'
--exec sp_addsrvrolemember 'test', 'sysadmin'
--exec sp_srvrolepermission
--exec SP_HELPSRVROLE
--exec SP_HELPSRVROLEMEMBER
--exec SP_HELPdbfixedrole
--exec SP_HELPROLE
--exec SP_HELPUSER
--exec sp_helplogins
--exec xp_logininfo
--exec sp_password  '12345678','12345678','dlm5'
