{pkgs}: {
  deps = [
    pkgs.glibcLocales
    pkgs.xorg.libXrandr
    pkgs.xorg.libXcomposite
    pkgs.xorg.libXcursor
    pkgs.xorg.libXi
    pkgs.xorg.libXtst
    pkgs.xorg.libXfixes
    pkgs.xorg.libXrender
    pkgs.xorg.libXext
    pkgs.xorg.libxcb
    pkgs.xorg.libX11
    pkgs.tk
    pkgs.tcl
    pkgs.qhull
    pkgs.pkg-config
    pkgs.gtk3
    pkgs.gobject-introspection
    pkgs.ghostscript
    pkgs.freetype
    pkgs.ffmpeg-full
    pkgs.cairo
  ];
}
