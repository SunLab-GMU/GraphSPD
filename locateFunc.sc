@main def exec(inputFile: String, outFile: String) = {
   importCode(inputFile)
   cpg.method.map(x=>(x.fullName,x.filename,x.lineNumber,x.lineNumberEnd)).toJson |> outFile
}