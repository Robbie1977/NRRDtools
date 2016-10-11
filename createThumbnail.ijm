args = split(getArgument(),",");
template=args[0];
signal=args[1];

//template="/robert/GIT/DrosAdultBRAINdomains/template/JFRCtemplate2010.nrrd"
//signal="/robert/GIT/DrosAdultBRAINdomains/individualDomainFiles/AdultBrainDomain0002.nrrd"
if (template=="") exit ("Missing template!");
if (signal=="") exit ("Missing signal!");
setBatchMode(true);
run("Nrrd ...", "load=[" + template + "]");
run("Multiply...", "value=0.5 stack");
run("Nrrd ...", "load=[" + signal + "]");
run("Multiply...", "value=2 stack");
ch1=File.getName(template);
ch2=File.getName(signal);
title=replace(replace(replace(replace(ch2,"ch2",""),"/",""),"VFBi","VFB_")," ","_");
run("Merge Channels...", "c1=" + ch1 + " c2=" + ch2 + " c3=" + ch1 + " create ignore");
run("Z Project...", "projection=[Max Intensity]");
getDimensions(width, height, channels, slices, frames); 
run("Scale...", "x=0.2 y=0.2 width=&width height=&height interpolation=Bicubic create title="+title);
file=replace(signal,ch2,"thumbnail.png");
imp = IJ.getImage(); 
final BufferedImage bi = create(imp); 
ImageIO.write(bi, "PNG", new File(file)); 
// saveAs("PNG", file);
run("Quit");
eval("script", "System.exit(0);"); 

public static BufferedImage create(final ColorProcessor src) { 
     if (src == null) { 
         throw new IllegalArgumentException("Input parameters are not valid: src=" + src ); 
     } 

     final ColorSpace cs = ColorSpace.getInstance(ColorSpace.CS_sRGB); 
     final int[] bits = {8, 8, 8, 8}; 
     final ColorModel cm = new ComponentColorModel(cs, bits, true, false, Transparency.BITMASK, DataBuffer.TYPE_BYTE); 
     final WritableRaster raster = cm.createCompatibleWritableRaster(src.getWidth(), src.getHeight()); 
     final DataBufferByte dataBuffer = (DataBufferByte) raster.getDataBuffer(); 

     final byte[] data = dataBuffer.getData(); 
     final int n = ((int[]) src.getPixels()).length; 
     final byte[] r = new byte[n]; 
     final byte[] g = new byte[n]; 
     final byte[] b = new byte[n]; 
     src.getRGB(r, g, b); 
     for (int i = 0; i < n; ++i) { 
         final int offset = i * 4; 
         data[offset] = r[i]; 
         data[offset + 1] = g[i]; 
         data[offset + 2] = b[i]; 
         data[offset + 3] = maxOf(r[i], maxOf(g[i],b[i])); 
     } 

     return new BufferedImage(cm, raster, false, null); 
} 
