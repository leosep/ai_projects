using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PhotoProcessor.Domain.Entities
{
    public class ProcessedImage
    {
        public System.Drawing.Bitmap Image { get; }
        public string FileName { get; }

        public ProcessedImage(System.Drawing.Bitmap image, string fileName)
        {
            Image = image ?? throw new ArgumentNullException(nameof(image));
            FileName = fileName ?? throw new ArgumentNullException(nameof(fileName));
        }
    }
}
