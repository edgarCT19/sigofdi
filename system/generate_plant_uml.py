import inspect
from mongoengine import Document, ReferenceField
from system import models  # Importa explícitamente tus modelos

def generar_plantuml():
    lines = [
        "@startuml",
        "hide circle",
        "skinparam linetype ortho",
        "skinparam entity {",
        "  BackgroundColor #EFF8FF",
        "  BorderColor #2B6CB0",
        "  FontName Arial",
        "}"
    ]

    # Solo obtener las clases que heredan de Document y están en system.models
    for name, cls in inspect.getmembers(models, inspect.isclass):
        if issubclass(cls, Document) and cls is not Document:
            lines.append(f"entity {cls.__name__} {{")
            for field_name, field in cls._fields.items():
                ftype = type(field).__name__
                lines.append(f"  {field_name} : {ftype}")
            lines.append("}\n")

    # Relaciones ReferenceField
    for name, cls in inspect.getmembers(models, inspect.isclass):
        if issubclass(cls, Document) and cls is not Document:
            for field_name, field in cls._fields.items():
                if isinstance(field, ReferenceField):
                    target = field.document_type.__name__
                    lines.append(f"{cls.__name__} --> {target} : {field_name}")

    lines.append("@enduml")
    return "\n".join(lines)


if __name__ == "__main__":
    with open("modelo_mongoengine.puml", "w", encoding="utf-8") as f:
        f.write(generar_plantuml())

    print("Archivo PlantUML generado: modelo_mongoengine.puml")