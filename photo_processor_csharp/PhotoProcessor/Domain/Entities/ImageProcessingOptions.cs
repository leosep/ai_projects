using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PhotoProcessor.Domain.Entities
{
    public class ImageProcessingOptions
    {
        public int TargetWidth { get; }
        public int TargetHeight { get; }
        public int Dpi { get; }
        public string HaarCascadePath { get; }

        public ImageProcessingOptions(int targetWidth, int targetHeight, int dpi, string haarCascadePath)
        {
            if (targetWidth <= 0 || targetHeight <= 0)
                throw new ArgumentException("El ancho y alto objetivo deben ser mayores que cero.");
            if (dpi <= 0)
                throw new ArgumentException("Los DPI deben ser mayores que cero.");
            if (string.IsNullOrWhiteSpace(haarCascadePath))
                throw new ArgumentException("La ruta del Haar Cascade no puede estar vacía.");

            TargetWidth = targetWidth;
            TargetHeight = targetHeight;
            Dpi = dpi;
            HaarCascadePath = haarCascadePath;
        }
    }

}
