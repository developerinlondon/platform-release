BEGIN{mx=0; my="0.0.0"}
/release\/[0-9]+\.[0-9]+\.[0-9]+/{split($2,a,".")
c=sprintf("%04d%04d%04d",a[1],a[2],a[3])
c=c+0
if (c > mx){mx=c;my=$2}}
END{split(my,a,".");print a[1] "." a[2]+1 "." a[3]}
