BEGIN{mx=0}
/\/tags\/[0-9]+\.[0-9]+\.[0-9]+/{split($3,a,".")
c=sprintf("%04d%04d%04d",a[1],a[2],a[3]);c=c+0
if (c > mx){mx=c;my=$3}}
END{print my}
