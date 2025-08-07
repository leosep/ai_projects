namespace PhotoProcessor.Application.UseCases
{
    using PhotoProcessor.Domain.Entities;
    using PhotoProcessor.Domain.Services;
    using System.Drawing;
    using System.Drawing.Imaging;
    using System.IO;
    using System.Threading.Tasks;

    public class ProcessImagesBatch
    {
        private readonly ImageProcessorService _imageProcessorService;

        public ProcessImagesBatch(ImageProcessorService imageProcessorService)
        {
            _imageProcessorService = imageProcessorService ?? throw new ArgumentNullException(nameof(imageProcessorService));
        }

        /// <summary>
        /// Ejecuta el procesamiento de un lote de imágenes desde un directorio de entrada a uno de salida.
        /// </summary>
        /// <param name="inputPath">Ruta del directorio de entrada de las fotos.</param>
        /// <param name="outputPath">Ruta del directorio donde se guardarán las fotos procesadas.</param>
        /// <param name="allowedExtensions">Extensiones de archivo permitidas para el procesamiento.</param>
        public async Task Execute(string inputPath, string outputPath, string[] allowedExtensions)
        {
            if (!System.IO.Directory.Exists(inputPath))
                throw new System.IO.DirectoryNotFoundException($"El directorio de entrada no existe: {inputPath}");
            if (!System.IO.Directory.Exists(outputPath))
                System.IO.Directory.CreateDirectory(outputPath); // Crea el directorio de salida si no existe.

            var files = System.IO.Directory.GetFiles(inputPath)
                                 .Where(file => allowedExtensions.Any(ext => file.ToLower().EndsWith(ext)))
                                 .OrderBy(f => f)
                                 .ToList();

            System.Console.WriteLine($"Encontrados {files.Count} archivos para procesar.");

            foreach (var file in files)
            {
                try
                {
                    System.Console.WriteLine($"Procesando: {System.IO.Path.GetFileName(file)}");
                    // Califica explícitamente System.Drawing.Image para resolver ambigüedad.
                    using (System.Drawing.Bitmap originalImage = (System.Drawing.Bitmap)System.Drawing.Image.FromFile(file))
                    {
                        var processedImage = _imageProcessorService.ProcessImageForID(originalImage, System.IO.Path.GetFileName(file));
                        string outputFilePath = System.IO.Path.Combine(outputPath, processedImage.FileName);
                        // Califica explícitamente System.Drawing.Imaging.ImageFormat para resolver ambigüedad.
                        processedImage.Image.Save(outputFilePath, System.Drawing.Imaging.ImageFormat.Jpeg); // Guardar en formato JPEG.
                        System.Console.WriteLine($"Guardado: {outputFilePath}");
                    }
                }
                catch (Exception ex)
                {
                    System.Console.Error.WriteLine($"Error al procesar el archivo {file}: {ex.Message}");
                }
                await System.Threading.Tasks.Task.Yield(); // Permite que el proceso de la consola no se bloquee.
            }
            System.Console.WriteLine("Proceso de conversión completado.");
        }
    }
}