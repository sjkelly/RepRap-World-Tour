h=5;
size=30;
gap=1;

width=0.4;

difference()
{
	rotate(45)
	cube([size,size,h],center=true);
	rotate(45)
	cube([size-2*width,size-2*width,h+1],center=true);

	for(i=[0:3])
	rotate(90*i)
	translate([size/2+gap+2*width,-0,0])
	cube([size,gap,h+1],center=true);
}

intersection()
{
	rotate(45)
	cube([size,size,h],center=true);
	rotate(45)
	cube([size-2*width,size-2*width,h],center=true);

	union()
	{
		for(i=[0:3])
		rotate(90*i)
		translate([size/2+gap+2*width,-0,0])
		difference()
		{
			cube([size+width*2,gap+width*2,h],center=true);
			cube([size,gap,h+1],center=true);
		}
	}
}