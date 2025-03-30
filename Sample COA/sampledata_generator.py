from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Image as REPLABImage
from PIL import Image, ImageDraw, ImageFont
import os
import sys


def create_pdf(filename, content, title, logo_path=None):
    """
    Generate PDF from structured content with enhanced description support
    
    Args:
    - filename: Output PDF file path
    - content: Dictionary of content sections
    - title: Document title
    - logo_path: Optional path to company logo image
    """
    doc = SimpleDocTemplate(filename, pagesize=letter, 
                            rightMargin=72, leftMargin=72, 
                            topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(name='CompanyHeader', 
                               parent=styles['Title'], 
                               fontSize=16, 
                               textColor=colors.darkblue,
                               alignment=1))  # center aligned
    
    # Add a style for descriptions
    styles.add(ParagraphStyle(name='Description', 
                               parent=styles['Normal'], 
                               fontSize=10, 
                               textColor=colors.darkgray,
                               spaceAfter=6))
    
    story = []
    
    # Add Company Logo if provided
    if logo_path:
        try:
            logo = REPLABImage(logo_path, width=2*inch, height=1*inch)
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 12))
        except Exception as e:
            print(f"Error loading logo: {e}")
    
    # Company Header
    story.append(Paragraph(content.get('company', 'Quality Assurance Report'), styles['CompanyHeader']))
    story.append(Spacer(1, 12))
    
    # Document Title
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 12))
    
    # Metadata Section
    if 'metadata' in content:
        metadata_style = styles['Normal']
        for key, value in content['metadata'].items():
            story.append(Paragraph(f"<b>{key}:</b> {value}", metadata_style))
        story.append(Spacer(1, 12))
    
    # Process each section
    for section in content.get('sections', []):
        # Section Header
        story.append(Paragraph(section['header'], styles['Heading2']))
        story.append(Spacer(1, 6))
        
        # Description (New addition)
        if 'description' in section:
            story.append(Paragraph(section['description'], styles['Description']))
            story.append(Spacer(1, 6))
        
        # Table Data
        if 'table' in section:
            table_data = section['table']
            table = Table(table_data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 12))
        
        # Additional Paragraphs
        if 'paragraphs' in section:
            for para in section['paragraphs']:
                story.append(Paragraph(para, styles['Normal']))
                story.append(Spacer(1, 6))
    
    # Certification Section
    if 'certification' in content:
        story.append(Paragraph("Certification", styles['Heading2']))
        cert_details = content['certification']
        for key, value in cert_details.items():
            story.append(Paragraph(f"<b>{key}:</b> {value}", styles['Normal']))
    
    # Build PDF
    doc.build(story)

def find_font(font_names):
    """
    Find an available font from a list of potential font names
    """
    # Common font locations
    font_paths = [
        # Windows
        r'C:\Windows\Fonts',
        # macOS
        '/Library/Fonts',
        '/System/Library/Fonts',
        # Linux
        '/usr/share/fonts',
        '/usr/local/share/fonts'
    ]

    # Try system-specific fonts
    system_fonts = {
        'windows': ['arial.ttf', 'arialbd.ttf', 'calibri.ttf'],
        'darwin': ['Arial.ttf', 'Arial Bold.ttf', 'Helvetica.ttf'],
        'linux': ['DejaVuSans.ttf', 'DejaVuSans-Bold.ttf']
    }

    # Get the current platform
    platform = sys.platform

    # Combine potential font names
    potential_fonts = (
        font_names + 
        (system_fonts.get(platform, []) if platform in system_fonts else [])
    )

    # Search for fonts
    for font_path in font_paths:
        for font_name in potential_fonts:
            full_path = os.path.join(font_path, font_name)
            if os.path.exists(full_path):
                return full_path
    
    # Fallback to default
    return None

def generate_document_image(content, filename, width=1700, height=2200):
    """
    Generate an image representation of a document
    
    Args:
    - content: Dictionary containing document content
    - filename: Output image file path
    - width: Image width (default 1700 pixels)
    - height: Image height (default 2200 pixels)
    """
    # Create a white background image
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Find and load fonts
    font_names = [
        'arial.ttf', 'arialbd.ttf', 'Arial.ttf', 'Arial Bold.ttf', 
        'Helvetica.ttf', 'DejaVuSans.ttf'
    ]
    
    def load_font(size, bold=False):
        font_path = find_font(font_names)
        if font_path:
            try:
                return ImageFont.truetype(font_path, size)
            except Exception as e:
                print(f"Error loading font: {e}")
        return ImageFont.load_default()
    
    # Load fonts
    title_font = load_font(40, bold=True)
    header_font = load_font(30, bold=True)
    normal_font = load_font(24)
    metadata_font = load_font(20)
    
    # Colors
    title_color = (0, 0, 139)  # Dark Blue
    header_color = (70, 70, 70)  # Dark Gray
    text_color = (0, 0, 0)  # Black
    
    # Margins and spacing
    left_margin = 100
    top_margin = 100
    line_spacing = 50
    
    # Current y-position
    y_pos = top_margin
    
    # Helper function to safely draw text
    def safe_draw_text(x, y, text, font, fill):
        try:
            # Encode text to handle Unicode characters
            safe_text = text.encode('utf-8', errors='ignore').decode('utf-8')
            draw.text((x, y), safe_text, font=font, fill=fill)
        except Exception as e:
            print(f"Error drawing text: {e}")
            draw.text((x, y), str(text), font=font, fill=fill)
    
    # Company Name
    safe_draw_text(left_margin, y_pos, 
                   content.get('company', 'Document'), 
                   title_font, 
                   title_color)
    y_pos += line_spacing * 2
    
    # Document Title
    safe_draw_text(left_margin, y_pos, 
                   filename.replace('.png', '').replace('_', ' ').title(), 
                   header_font, 
                   header_color)
    y_pos += line_spacing * 2
    
    # Metadata
    if 'metadata' in content:
        for key, value in content['metadata'].items():
            safe_draw_text(left_margin, y_pos, 
                           f"{key}: {value}", 
                           metadata_font, 
                           text_color)
            y_pos += line_spacing
        y_pos += line_spacing
    
    # Sections
    for section in content.get('sections', []):
        # Section Header
        safe_draw_text(left_margin, y_pos, 
                       section['header'], 
                       header_font, 
                       header_color)
        y_pos += line_spacing * 1.5
        
        # Table Data
        if 'table' in section:
            table_data = section['table']
            col_width = 300
            cell_height = 50
            
            for row_idx, row in enumerate(table_data):
                # Alternate row background
                if row_idx > 0:
                    row_fill_color = (240, 240, 240) if row_idx % 2 == 0 else (255, 255, 255)
                    draw.rectangle([left_margin, y_pos, left_margin + (col_width * len(row)), y_pos + cell_height], 
                                   fill=row_fill_color)
                
                # Draw row data
                for col_idx, cell in enumerate(row):
                    cell_font = header_font if row_idx == 0 else normal_font
                    cell_color = header_color if row_idx == 0 else text_color
                    safe_draw_text(left_margin + (col_width * col_idx), y_pos, 
                                   str(cell), 
                                   cell_font, 
                                   cell_color)
                
                y_pos += cell_height
            
            y_pos += line_spacing
        
        # Additional Paragraphs
        if 'paragraphs' in section:
            for para in section['paragraphs']:
                safe_draw_text(left_margin, y_pos, 
                               para, 
                               normal_font, 
                               text_color)
                y_pos += line_spacing
            y_pos += line_spacing
    
    # Certification Section
    if 'certification' in content:
        safe_draw_text(left_margin, y_pos, 
                       "Certification", 
                       header_font, 
                       header_color)
        y_pos += line_spacing * 1.5
        
        for key, value in content['certification'].items():
            safe_draw_text(left_margin, y_pos, 
                           f"{key}: {value}", 
                           normal_font, 
                           text_color)
            y_pos += line_spacing
    
    # Save the image
    image.save(filename)
    print(f"Image saved: {filename}")

# Manufacturer Batch Results Content
manufacturer_content = {
    "company": "LifeScience Pharmaceuticals",
    "metadata": {
        "Batch Reference": "MFG-2024-0328",
        "Product": "Pharmaceutical Grade Sodium Chloride",
        "Test Date": "March 29, 2024",
        "Testing Department": "Quality Assurance Lab"
    },
    "sections": [
        {
            "header": "Physical Characteristics Analysis",
            "description": "The physical characteristics of our Pharmaceutical Grade Sodium Chloride undergo meticulous evaluation to ensure consistent quality and performance. Our comprehensive testing protocols assess critical parameters that directly impact the material's pharmaceutical applications and manufacturing reliability.",
            "table": [
                ["Parameter", "Specification", "Test Result", "Status"],
                ["Appearance", "White, crystalline powder", "White, crystalline powder", "✓ PASS"],
                ["Particle Size", "100-200 μm", "190 μm", "✓ PASS"],
                ["Bulk Density", "0.85-0.95 g/mL", "0.92 g/mL", "✓ PASS"]
            ]
        },
        {
            "header": "Chemical Analysis",
            "description": "Our advanced chemical analysis employs precision techniques to verify the purity, composition, and chemical stability of sodium chloride. Each analytical test is conducted with stringent methodology to meet pharmaceutical-grade material requirements and ensure exceptional product quality.",
            "table": [
                ["Test", "Specification", "Result", "Status"],
                ["Purity", "≥ 99.5%", "99.6%", "✓ PASS"],
                ["Moisture Content", "≤ 0.1%", "0.08%", "✓ PASS"],
                ["Heavy Metals", "≤ 10 ppm", "5.5 ppm", "✓ PASS"],
                ["pH (1% Solution)", "6.5-7.5", "7.1", "✓ PASS"]
            ]
        },
        {
            "header": "Microbiological Testing",
            "description": "Microbiological testing is crucial in validating the safety and sterility of our pharmaceutical-grade sodium chloride. Our comprehensive screening process utilizes advanced detection methods to identify and eliminate potential microbial contamination, ensuring the highest standards of microbiological purity.",
            "table": [
                ["Parameter", "Specification", "Result", "Status"],
                ["Total Aerobic Count", "≤ 100 CFU/g", "<15 CFU/g", "✓ PASS"],
                ["Total Yeast & Mold", "≤ 10 CFU/g", "<8 CFU/g", "✓ PASS"],
                ["Absence of Pathogens", "Negative", "Negative", "✓ PASS"]
            ]
        }
    ],
    "certification": {
        "Tested By": "Jane Doe, Senior Analyst",
        "Reviewed By": "Dr. Michael Chen, QA Director", 
        "Certification Date": "March 29, 2024"
    }
}

# Supplier Certificate of Analysis Content
supplier_content = {
    "company": "PureChemicals Incorporated",
    "metadata": {
        "Lot/Batch Number": "PC2024-0328",
        "Product": "Pharmaceutical Grade Sodium Chloride", 
        "Date of Manufacture": "March 15, 2024",
        "Date of Analysis": "March 28, 2024"
    },
    "sections": [
        {
            "header": "Physical Characteristics",
            "description": "The physical characteristics of our Pharmaceutical Grade Sodium Chloride have been meticulously evaluated to ensure optimal quality and performance. Our rigorous testing protocols focus on critical parameters that impact the material's usability and consistency in pharmaceutical applications.",
            "table": [
                ["Parameter", "Specification", "Test Result", "Method"],
                ["Appearance", "White, crystalline powder", "Complies", "Visual Inspection"],
                ["Particle Size", "100-200 μm", "185 μm", "Laser Diffraction"],
                ["Bulk Density", "0.85-0.95 g/mL", "0.90 g/mL", "ASTM B212"]
            ]
        },
        {
            "header": "Chemical Analysis", 
            "description": "Our chemical analysis employs state-of-the-art analytical techniques to verify the purity, composition, and chemical stability of the sodium chloride. Each test is conducted with precision to meet the stringent requirements of pharmaceutical-grade materials.",
            "table": [
                ["Test", "Specification", "Result", "Acceptance Criteria"],
                ["Purity", "≥ 99.5%", "99.7%", "Titration Method"],
                ["Moisture Content", "≤ 0.1%", "0.07%", "Karl Fischer"],
                ["Heavy Metals", "≤ 10 ppm", "5.2 ppm", "ICP-MS"],
                ["pH (1% Solution)", "6.5-7.5", "7.2", "Potentiometric"]
            ]
        },
        {
            "header": "Microbiological Testing",
            "description": "Microbiological testing is critical to ensure the safety and sterility of our pharmaceutical-grade sodium chloride. Our comprehensive screening process identifies and eliminates potential microbial contamination.",
            "table": [
                ["Parameter", "Specification", "Result", "Method"],
                ["Total Aerobic Count", "≤ 100 CFU/g", "<10 CFU/g", "USP <61>"],
                ["Total Yeast & Mold", "≤ 10 CFU/g", "<5 CFU/g", "USP <62>"],
                ["Absence of Pathogens", "Negative", "Negative", "PCR Screening"]
            ]
        }
    ],
    "certification": {
        "Authorized Signature": "Digital Signature Verified",
        "Quality Control Manager": "John Smith", 
        "Certification Date": "March 28, 2024"
    }
}
# Compliance Comparison Certificate Content
compliance_content = {
    "company": "LifeScience Pharmaceuticals",
    "metadata": {
        "Batch Reference": "MFG-2024-0328",
        "Supplier Batch": "PC2024-0328",
        "Product": "Pharmaceutical Grade Sodium Chloride",
        "Comparison Date": "March 30, 2024"
    },
    "sections": [
        {
            "header": "Physical Characteristics Comparison",
            "description": "A comprehensive comparative analysis of physical characteristics was conducted to validate the consistency and quality of the pharmaceutical-grade sodium chloride between the supplier and manufacturer. The evaluation focused on critical parameters that directly impact material performance and usability.",
            "table": [
                ["Parameter", "Supplier Result", "Manufacturer Result", "Status"],
                ["Appearance", "Complies", "White, crystalline powder", "✓ MATCH"],
                ["Particle Size", "185 μm", "190 μm", "✓ WITHIN TOLERANCE"],
                ["Bulk Density", "0.90 g/mL", "0.92 g/mL", "✓ WITHIN TOLERANCE"]
            ]
        },
        {
            "header": "Chemical Analysis Comparison",
            "description": "The chemical analysis comparison demonstrates exceptional alignment between supplier and manufacturer results. Precision analytical techniques were employed to evaluate critical chemical properties, ensuring the sodium chloride meets the highest pharmaceutical-grade standards.",
            "table": [
                ["Test", "Supplier Result", "Manufacturer Result", "Status"],
                ["Purity", "99.7%", "99.6%", "✓ COMPLIANT"],
                ["Moisture Content", "0.07%", "0.08%", "✓ COMPLIANT"],
                ["Heavy Metals", "5.2 ppm", "5.5 ppm", "✓ COMPLIANT"],
                ["pH (1% Solution)", "7.2", "7.1", "✓ COMPLIANT"]
            ]
        },
        {
            "header": "Microbiological Testing Comparison",
            "description": "Microbiological testing comparison validated the stringent sterility and safety standards maintained by both the supplier and manufacturer. Advanced screening methods confirmed minimal microbial presence and total absence of pathogens.",
            "table": [
                ["Parameter", "Supplier Result", "Manufacturer Result", "Status"],
                ["Total Aerobic Count", "<10 CFU/g", "<15 CFU/g", "✓ COMPLIANT"],
                ["Total Yeast & Mold", "<5 CFU/g", "<8 CFU/g", "✓ COMPLIANT"],
                ["Absence of Pathogens", "Negative", "Negative", "✓ MATCH"]
            ]
        },
        {
            "header": "Compliance Summary",
            "description": "A comprehensive evaluation of batch comparison results reveals consistent quality and full compliance with established pharmaceutical manufacturing standards.",
            "paragraphs": [
                "Overall Compliance: FULLY COMPLIANT",
                "Variation Tolerance: Within Acceptable Limits",
                "Batch Approval Status: APPROVED"
            ]
        }
    ],
    "certification": {
        "Certified By": "Automated Compliance Verification System",
        "Reviewed By": "Dr. Emily Rodriguez, Compliance Officer",
        "Certification Number": "MFG-2024-0328-COMP",
        "Certification Date": "March 30, 2024"
    }
}

# Generate PDFs
create_pdf('manufacturer_batch_results.pdf', manufacturer_content, 'Manufacturer Batch Test Report','D:/Tejash/GenAI Project - CoA/Novartis-Emblem.png')
create_pdf('supplier_certificate.pdf', supplier_content, 'Supplier Certificate of Analysis','D:\Tejash\GenAI Project - CoA\PURE-3.jpg')
create_pdf('compliance_comparison.pdf', compliance_content, 'Comparative Compliance Certificate','D:/Tejash/GenAI Project - CoA/Novartis-Emblem.png')
print("PDFs generated successfully!")

# Generate images using the same content from previous PDF script
generate_document_image(manufacturer_content, 'manufacturer_batch_results.png')
generate_document_image(supplier_content, 'supplier_certificate.png')
generate_document_image(compliance_content, 'compliance_comparison.png')

print("Images generated successfully!")