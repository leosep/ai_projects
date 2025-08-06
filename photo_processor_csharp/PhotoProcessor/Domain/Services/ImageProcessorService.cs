namespace PhotoProcessor.Domain.Services
{
    // Importa las entidades del dominio.
    using PhotoProcessor.Domain.Entities;
    // Importa las librerías de Emgu.CV para procesamiento de imágenes.
    using Emgu.CV;
    //using Emgu.CV.BitmapExtension; // Necesario para el método de extensión ToMat()
    // Importa las librerías de System.Drawing para manipulación de imágenes.
    using System.Drawing;
    using System.Linq; // Necesario para operaciones LINQ como OrderByDescending

    // Servicio de dominio para el procesamiento de imágenes.
    public class ImageProcessorService
    {
        private readonly CascadeClassifier _faceCascade;
        private readonly ImageProcessingOptions _options;

        public ImageProcessorService(ImageProcessingOptions options)
        {
            _options = options ?? throw new ArgumentNullException(nameof(options));
            try
            {
                // Inicializa el clasificador de caras con la ruta proporcionada.
                _faceCascade = new CascadeClassifier(_options.HaarCascadePath);
            }
            catch (Exception ex)
            {
                // Lanza una excepción si hay un error al cargar el Haar Cascade.
                throw new InvalidOperationException($"Error al cargar Haar Cascade: {ex.Message}\nAsegúrese de que '{_options.HaarCascadePath}' está en el directorio de la aplicación.", ex);
            }
        }

        /// <summary>
        /// Procesa una imagen para fotos de identificación, detectando y centrando el rostro.
        /// </summary>
        /// <param name="originalImage">La imagen original en formato Bitmap.</param>
        /// <param name="fileName">El nombre del archivo de la imagen original.</param>
        /// <returns>Un objeto ProcessedImage que contiene la imagen procesada.</returns>
        public ProcessedImage ProcessImageForID(System.Drawing.Bitmap originalImage, string fileName)
        {
            if (originalImage == null)
                throw new ArgumentNullException(nameof(originalImage));

            // Convierte System.Drawing.Bitmap a Emgu.CV.Mat para procesamiento con Emgu.CV.
            Mat imgMat;
            using (System.Drawing.Bitmap bmp = new System.Drawing.Bitmap(originalImage))
            {
                imgMat = bmp.ToMat(); // Utiliza el método de extensión ToMat()
            }

            // Convierte la imagen a escala de grises para la detección de rostros.
            Mat grayImg = new Mat();
            CvInvoke.CvtColor(imgMat, grayImg, Emgu.CV.CvEnum.ColorConversion.Bgr2Gray);
            CvInvoke.EqualizeHist(grayImg, grayImg);

            // Detecta caras en la imagen.
            Rectangle[] faces = _faceCascade.DetectMultiScale(grayImg, 1.1, 20, new System.Drawing.Size(100, 100));

            System.Drawing.Bitmap finalProcessedImage;

            if (faces.Length > 0)
            {
                // Selecciona la cara más grande para el procesamiento.
                Rectangle faceRect = faces.OrderByDescending(f => f.Width * f.Height).First();

                // Calcula el relleno alrededor de la cara para incluir hombros y espacio para la cabeza.
                int paddingX = (int)(faceRect.Width * 0.7);
                int paddingY = (int)(faceRect.Height * 0.7);

                // Calcula el rectángulo de recorte final, asegurando que no exceda los límites de la imagen original.
                int cropX = Math.Max(0, faceRect.X - paddingX);
                int cropY = Math.Max(0, faceRect.Y - paddingY);
                int cropWidth = Math.Min(originalImage.Width - cropX, faceRect.Width + (2 * paddingX));
                int cropHeight = Math.Min(originalImage.Height - cropY, faceRect.Height + (2 * paddingY));
                System.Drawing.Rectangle finalCropRect = new System.Drawing.Rectangle(cropX, cropY, cropWidth, cropHeight);

                // Recorta la imagen.
                using (System.Drawing.Bitmap croppedBmp = new System.Drawing.Bitmap(finalCropRect.Width, finalCropRect.Height))
                {
                    using (System.Drawing.Graphics g = System.Drawing.Graphics.FromImage(croppedBmp))
                    {
                        g.DrawImage(originalImage, new System.Drawing.Rectangle(0, 0, croppedBmp.Width, croppedBmp.Height), finalCropRect, System.Drawing.GraphicsUnit.Pixel);
                    }
                    // Redimensiona la imagen recortada a las dimensiones objetivo.
                    finalProcessedImage = ResizeImageProportionally(croppedBmp, _options.TargetWidth, _options.TargetHeight);
                }
            }
            else
            {
                // Si no se detecta rostro, se redimensiona la imagen completa a las dimensiones objetivo.
                finalProcessedImage = ResizeImageProportionally(originalImage, _options.TargetWidth, _options.TargetHeight);
            }

            // Configura los DPI de la imagen procesada.
            finalProcessedImage.SetResolution(_options.Dpi, _options.Dpi);

            return new ProcessedImage(finalProcessedImage, fileName);
        }

        /// <summary>
        /// Redimensiona una imagen proporcionalmente para ajustarse a las dimensiones máximas especificadas.
        /// </summary>
        /// <param name="originalImage">La imagen original.</param>
        /// <param name="maxWidth">El ancho máximo deseado.</param>
        /// <param name="maxHeight">El alto máximo deseado.</param>
        /// <returns>Una nueva imagen Bitmap redimensionada proporcionalmente.</returns>
        private System.Drawing.Bitmap ResizeImageProportionally(System.Drawing.Bitmap originalImage, int maxWidth, int maxHeight)
        {
            int originalWidth = originalImage.Width;
            int originalHeight = originalImage.Height;

            float ratioX = (float)maxWidth / originalWidth;
            float ratioY = (float)maxHeight / originalHeight;
            float ratio = Math.Min(ratioX, ratioY); // Usa el ratio más pequeño para asegurar que la imagen quepa dentro de las dimensiones.

            int newWidth = (int)(originalWidth * ratio);
            int newHeight = (int)(originalHeight * ratio);

            System.Drawing.Bitmap newImage = new System.Drawing.Bitmap(newWidth, newHeight);
            using (System.Drawing.Graphics g = System.Drawing.Graphics.FromImage(newImage))
            {
                g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic;
                g.DrawImage(originalImage, 0, 0, newWidth, newHeight);
            }
            return newImage;
        }
    }
}