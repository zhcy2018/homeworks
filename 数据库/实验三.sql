/*
CREATE TABLE S(Sno NVARCHAR(10) NOT NULL PRIMARY KEY,
                Sname NVARCHAR(10), Ssex nvarchar(1),
               Sage SMALLINT, Sdept NVARCHAR(50),Schoolship money null);
CREATE TABLE C(Cno nvarchar(10) NOT NULL PRIMARY KEY,
               Cname nvarchar(15),Pno nvarchar(15),Ccredit decimal(4,1) );
CREATE TABLE SC(Sno nvarchar(10) not null foreign key references S(Sno),
                 Cno nvarchar(10) not null foreign key references C(Cno)Primary Key(Sno,Cno),
                 Grade decimal(5,1));
CREATE TABLE C_Plan(Cno nvarchar(10) NULL ,
               Mclass nvarchar(4) null,Mno nvarchar(10) null,Syear varchar(4) ,
               Term nvarchar(3) null , StudentNum int null);
CREATE TABLE C_Teacher(Tno nvarchar(15) NULL,
                 Cno nvarchar(10) null,
                 Mclass varchar(4) null ,Mno nvarchar(10) null,Syear varchar(4) null,StudentNum int null);
 
              
              

declare @i int
declare @c int 
set @i=1 
set @c=69

while @i<@c 
begin 
insert into S select top (1) Sno,sname,ssex,Sage,Sdept,FLOOR(RAND()*1000) from SM1.dbo.S where  Sno not in (select top (@i)  Sno from SM1.dbo.S order by Sno) order by Sno;
set @i=@i+1 
END

insert into C select * from SM1.DBO.C

delete from SC

declare @i int
declare @c int 
set @i=1 

while @i<6 
begin 
insert into SC(Cno,Sno,Grade) select cno,a.Sno,FLOOR(RAND()*100) from SM1.dbo.C,(select top (1) Sno from SM1.dbo.S where  Sno not in (select top (@i)  Sno from SM1.dbo.S order by Sno) order by Sno)a;
set @i=@i+1 
END
*/
--insert into SC(Cno,Sno,Grade) select cno,a.Sno,FLOOR(RAND()*100) from SM1.dbo.C,(select top (1) Sno from SM1.dbo.S where  Sno not in (select top (@i)  Sno from SM1.dbo.S order by Sno) order by Sno)a;
--select top (@i) Sno,sname,ssex,Sage,Sdept,FLOOR(RAND()*1000) from SM1.dbo.S where  Sno not in (select top (@i)  Sno from SM1.dbo.S order by Sno) order by Sno;
--select top (@i)  Sno from SM1.dbo.S order by Sno
/*
	IF(@age<150)
		Begin
			update
			Select ID, Name, Age, AddDate From inserted
		End
	ELSE
		Begin
		    print('年龄应小于150')
			rollback transaction     --数据回滚
		END
*/
/*
Create TRIGGER [dbo].[tri_upd_S]
   ON  [dbo].[S]
   AFTER update
AS 
BEGIN
	
	SET NOCOUNT ON;

	Declare @sno varchar(10);
	Declare @Osno varchar(10);
	Select @sno=sno  From inserted
	Select @Osno=sno  From deleted
	update SC SET Sno=@sno WHERE Sno=@Osno
END

Create TRIGGER [dbo].[tri_upd_S1]
   ON  [dbo].[S]
   instead of update
AS 
BEGIN
	
	SET NOCOUNT ON;

	Declare @sno varchar(10);
	Declare @Osno varchar(10);
	Select @sno=sno  From inserted
	Select @Osno=sno  From deleted
	update SC SET Sno=@sno WHERE Sno=@Osno
	update S SET Sno=@sno WHERE Sno=@Osno
END
*/
/*
Create TRIGGER [dbo].[tri_no_upd_S]
   ON  [dbo].[S]
   instead of delete
AS 
BEGIN
	SET NOCOUNT ON;
	Declare @sno varchar(10);
	select @sno=sno from deleted
	delete from SC where Sno=@sno
	delete from S where Sno=@sno
END

delete from S WHERE SNO='2017300870'
*/
/*
Create TRIGGER [dbo].[tri_ins_jxjh]
   ON  [dbo].[C_Plan]
   instead of INSERT
AS 
BEGIN
	SET NOCOUNT ON;
	Declare @Cno varchar(10);
	Declare @Tno varchar(10);
	select @Cno=cno from inserted
	SET @Tno='T2020'+@Cno
	INSERT INTO C_Plan select *from inserted
	INSERT INTO C_teacher select @Tno,Mclass,Mno,Syear,Syear,StudentNum from inserted
END
Create TRIGGER [dbo].[tri_ins_jxjh1]
   ON  [dbo].[C_Plan]
   after INSERT
AS 
BEGIN
	SET NOCOUNT ON;
	Declare @Cno varchar(10);
	Declare @Tno varchar(10);
	select @Cno=cno from inserted
	SET @Tno='T2020'+@Cno
	--INSERT INTO C_Plan select *from inserted
	INSERT INTO C_teacher select @Tno,Mclass,Mno,Syear,Syear,StudentNum from inserted
END
insert into C_plan values(1,1,1,1,1,1)
select * from C_Teacher
*//*
Create TRIGGER [dbo].[tri_ins_jxjh1]
   ON  [dbo].[C_Plan]
   after delete
AS 
BEGIN
	SET NOCOUNT ON;
	Declare @Cno varchar(10);
	Declare @Tno varchar(10);
	select @Cno=cno from deleted
	SET @Tno='T2020'+@Cno
	--INSERT INTO C_Plan select *from inserted
	delete from  C_teacher where Tno=@Tno
END
*/
--drop trigger tri_ins_jxjh1
/*
Create TRIGGER [dbo].[del_tri_CourPlan]
   ON  [dbo].[C_Plan]
   after delete
AS 
BEGIN
	SET NOCOUNT ON;
	Declare @Cno varchar(10);
	Declare @Tno varchar(10);
	select @Cno=cno from deleted
	SET @Tno='T2020'+@Cno
	delete from  C_teacher where Tno=('T2020'+@Cno)
END
Create TRIGGER [dbo].[del_tri_CourPlan1]
   ON  [dbo].[C_Plan]
   instead of delete
AS 
BEGIN
	SET NOCOUNT ON;
	Declare @Cno varchar(10);
	Declare @Tno varchar(10);
	select @Cno=cno from deleted
	SET @Tno='T2020'+@Cno
	delete from  C_teacher where Tno=('T2020'+@Cno)
	delete from C_Plan where Cno=@Cno
END
delete from C_plan where cno='1'
delete from C_teacher
insert into c_plan values(1,1,1,1,1,1)
delete from C_plan where cno=1
select*from C_Plan
select*from C_Teacher
*/
/*
Create TRIGGER [dbo].[tri_no_updCno]
   ON  [dbo].[C_Plan]
   instead of update
AS 
BEGIN
	SET NOCOUNT ON;
	Declare @Cno varchar(10);Declare @Ocno varchar(10);
	select @Ocno=cno from deleted;select @Cno=cno from inserted
	if @Cno=@Ocno
	begin
		insert into c_Plan select *from inserted
	end
	else
	begin
		print('不可修改')
	end
END
Create TRIGGER [dbo].[tri_no_updCno1]
   ON  [dbo].[C_Plan]
   instead of update
AS 
BEGIN
	SET NOCOUNT ON;
	Declare @Cno varchar(10);Declare @Ocno varchar(10);
	select @Ocno=cno from deleted;select @Cno=cno from inserted
	if @Cno=@Ocno
	begin
		insert into c_Plan select *from inserted
	end
	else
	begin
		print('不可修改');rollback transaction 
	end
END
*/
/*
Create TRIGGER [dbo].[tri_no_updCno]
   ON  [dbo].[C_Plan]
   instead of update
AS 
BEGIN
	SET NOCOUNT ON;
	Declare @Cno varchar(10);Declare @Ocno varchar(10);
	Declare @term varchar(10);Declare @Oterm varchar(10);
	select @Ocno=cno from deleted;select @Cno=cno from inserted
	select @Oterm=term from deleted;select @term=term from inserted
	if @Cno=@Ocno and @Oterm=@term
	begin
		insert into c_Plan select *from inserted
	end
	else
	begin
		print('不可修改')
	end
END

ALTER  TABLE  C_Plan  DISABLE  TRIGGER tri_no_updCno
ALTER  TABLE  C_Plan  ENABLE  TRIGGER tri_no_updCno
DROP TRIGGER tri_no_updCno
*/

CREATE TRIGGER DDL_TableTrigger
ON DATABASE
FOR DROP_TABLE, ALTER_TABLE
AS
BEGIN
   PRINT ('禁止操作')
   ROLLBACK ;
end

drop table C_Teacher;