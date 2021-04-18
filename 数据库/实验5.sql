-- For this expriment, some problems need two process to be solved. Part1 is which runs in a process, 
-- and of course part2 is which runs in another process
-- Some process may be lost but most of it can be indicate from the context


-- part 1
/*
begin transaction
  set transaction isolation level read uncommitted
      select id from test
      update test set id=6 where id=5
      select id from test
  commit;
  */
  /*
  begin transaction
  set transaction isolation level read uncommitted
      select id from test
      insert into test values(1)
      select id from test
  commit;
  */
  /*
    begin transaction
  --set transaction isolation level read uncommitted
      select id from test
      insert into test with(holdlock) values(1) ;
      select id from test
  commit;
  */
  /*
      begin transaction
  set transaction isolation level serializable
      select id from test
      insert into test  values(1)
      select id from test
  commit;
  */
  /*
        begin transaction
  --set transaction isolation level serializable
      select  id  from test with(Xlock);
      select  *  from S with(Xlock);
  commit;
  */
  
 -- part2
  /*
CREATE FUNCTION f_NextBH()
RETURNS char(8)
AS
BEGIN
 RETURN(SELECT 'MJBNB'+RIGHT(1000001+ISNULL(RIGHT(MAX(BH),6),0),6) FROM tb WITH(XLOCK,PAGLOCK))
END
GO
*/
--SELECT datediff(ss,'1970-01-01',GETDATE())
--select REPLICATE ('i',32)+'fwefewfw';
/*
create Function pad()
returns char(32)
as
begin
declare @i char(32);
declare @count int;
SELECT @i=datediff(ss,'1970-01-01',GETDATE());
select @count=(30-len(@i));
return (select 'OD'+REPLICATE('0',@count)+@i);
end


create Function pad_1()
returns char(32)
as
begin
declare @i char(32);
declare @count int;
SELECT @i=datediff(ss,'1970-01-01',GETDATE());
select @count=(30-len(@i));
return (select 'ID'+REPLICATE('0',@count)+@i);
end


create table BANK(
	BID char(32),
	Sno char(32),
	MoneyNum money 
);

create table TranFlowIn(
	InID char(32),
	FromID char(32),
	TranMoney money,
	Getime TIME,
	TFINID char(32) DEFAULT DBO.pad()
	
);
create table TranFlowOut(
	InID char(32),
	FromID char(32),
	TranMoney money,
	Getime TIME,
	TFOUTID char(32) DEFAULT DBO.pad_1(),
);


begin tran TranStart
insert into TranFlowIn(InID,FromID,TranMoney,Getime) values('B20210506004','B20200506001',20.21,GETDATE());
if @@ERROR<>0
	rollback tran TranStart
else
begin
	insert into TranFlowOut(InID,FromID,TranMoney,Getime) values('B20210506004','B20200506001',20.21,GETDATE());
	if @@ERROR<>0
	begin
		rollback tran TranStart
	end
	else
	begin
		update BANK set MoneyNUm = MoneyNUm-20.21 where sno='2017300647'
		if @@ERROR<>0
		begin
			rollback tran TranStart
		end
		else
		begin
			update BANK set MoneyNUm = MoneyNUm-20.21 where sno='2017300647'
			if @@ERROR<>0
			begin
				rollback tran TranStart
			end
			else
			begin
				update BANK set MoneyNUm = MoneyNUm+20.21 where sno='2020302206'
				if @@ERROR<>0
				begin
					rollback tran TranStart
				end
				else
				begin
					commit tran TranStart
				end
			end
		end
	end
end
*/
--delete from test where ID=1
/*
begin transaction
  set transaction isolation level read uncommitted
      select id from test
      update test set id=6 where id=5
      select id from test
  commit;
*/
/*
    begin transaction
  --set transaction isolation level read uncommitted
      select id from test
      insert into test with(holdlock) values(1)
      select id from test
  commit;
*/  
/*
    begin transaction
  set transaction isolation level serializable
      select id from test
      insert into test  values(1)
      select id from test
  commit;
  */
  /*
          begin transaction
  --set transaction isolation level serializable
      
      select  *  from S with(Xlock);
      select  id  from test with(Xlock);
  commit;
  */