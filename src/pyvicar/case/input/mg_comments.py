from pyvicar._format import write_banner


def write_mg_comment(f):
    write_banner(f, "Comments for MG Method")
    f.write("1. Iterations per loop\n")
    f.write(
        "   iterFinest is used for controling the number of loops at the finest level.\n"
    )
    f.write(
        "   iterCoarest is used for controling the number of loops at the coarest level.\n"
    )
    f.write(
        "   iterInter is used for other levels. If use value 0, then the number of loops will increase linearly.\n"
    )
    f.write(
        "   Tips:  1   1   1 must be used for GCM method. You may use 2 1 30 or 1 1 30 for SSM.\n"
    )
    f.write("2. total # of grid levels\n")
    f.write(
        "   0 is set by the Code, can work for most cases. Other values will be the user defined levels. You could\n"
    )
    f.write("   decide how many level can be chosen at each direction. \n")
    f.write("3. Omega\n")
    f.write("   1.0 for 2D case, better use 1.5 for 3D case. \n")
