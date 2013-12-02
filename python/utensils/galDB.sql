
/*** 
mysql script to create a database of galaxies taken from a text catalogue of galaxy quantities. 
The specific catalogue used in this example is taken partly from the DES mocks (ra, dec, redshift, shear) and partly from the catsim galaxy catalogue created from the Millenium simulation mocks (all other quantities). 
Note that we are creating bulge+disk galaxies, and that each component (bulge, disk) is a separate entry in the table. 
***/

/*** this is the name of your database. Change it to whatever you want. ***/
use djbard_galaxies;

/*** this is the name of the table you are creating inside the database***/
CREATE TABLE galaxiesTest(
	htmid bigint NOT NULL, 
	ra float NULL, 
	decl float NULL, 
	redshift float NULL,
	av_b float NULL, 
	rv_b float NULL, 
	ext_model_b varchar(10) NULL, 
	av_d float NULL, 
	rv_d float NULL,  
	ext_model_d varchar(10) NULL,
	pa_bulge float NULL, 
	pa_disk float NULL, 
	a_b float NULL, 
	b_b float NULL, 
	bulge_n float NULL,
	a_d float NULL, 
	b_d float NULL, 
	disk_n float NULL,
	magnorm_bulge float NULL, 
	magnorm_disk float NULL, 
	magnorm_agn float NULL, 
	sedname_agn varchar(50) NULL,
	sedname_bulge varchar(50) NULL, 
	sedname_disk varchar(50) NULL, 
	id int NOT NULL, 
	shear1 float NULL, 
	shear2 float NULL, 
	kappa float NULL, 

PRIMARY KEY CLUSTERED 
(
	htmid ASC,
	id ASC
)
);


/*** Load the data into the table you've just created***/
LOAD DATA LOCAL INFILE 'galDB.dat' INTO TABLE galaxiesTest FIELDS TERMINATED BY ' ' ;

/*** The sed file names require some updating to make them compatible with the latest SEDs used in phosim. 
If the galaxy component is a bulge(disk) then there is no sed name associated with it, and the corresponding quantity needs to be set to 'NULL' in the databse. 
You may use this later on to distinguish between bulge and disk components. 
 ***/
update galaxiesTest set sedname_bulge = NULL where sedname_bulge='N';
update galaxiesTest set sedname_disk = NULL where sedname_disk='N';
update galaxiesTest set sedname_disk=replace(substring_index(sedname_disk,'/',-1), '.gz', '') where sedname_disk is not NULL;
update galaxiesTest set sedname_bulge=replace(substring_index(sedname_bulge,'/',-1), '.gz', '') where sedname_bulge is not NULL;

/***
If you have your ra/dec in radians, you'll need to convert them to degrees to match the conventions. 
***/
update galaxiesTest set decl = decl *(180.0/3.1415926);
update galaxiesTest set ra = ra *(180.0/3.1415926);