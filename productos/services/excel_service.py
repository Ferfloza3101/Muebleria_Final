
# Archivo para crear Excel (xlsx).
# Usa xlsxwriter y devuelve el archivo en memoria.

from io import BytesIO
from datetime import datetime

import xlsxwriter


class ExcelExportService:

	@staticmethod
	def build_workbook(headers, rows, title="Reporte") -> bytes:
		# remove_timezone evita errores con fechas con zona horaria.
		buffer = BytesIO()
		workbook = xlsxwriter.Workbook(buffer, {"in_memory": True, "remove_timezone": True})
		worksheet = workbook.add_worksheet(title[:31])  # nombre de hoja (máx 31)

		# formatos básicos
		header_fmt = workbook.add_format({
			"bold": True,
			"bg_color": "#F2F2F2",
			"bottom": 1,
			"align": "center",
			"valign": "vcenter",
		})
		text_fmt = workbook.add_format({"font_size": 10})
		num_fmt = workbook.add_format({"num_format": "#,##0.00", "font_size": 10})
		int_fmt = workbook.add_format({"num_format": "#,##0", "font_size": 10})
		date_fmt = workbook.add_format({"num_format": "yyyy-mm-dd hh:mm", "font_size": 10})

		# escribe encabezados
		for col, header in enumerate(headers):
			worksheet.write(0, col, header, header_fmt)

		# escribe filas
		for row_idx, row in enumerate(rows, start=1):
			for col_idx, value in enumerate(row):
				cell_fmt = text_fmt
				if isinstance(value, (int,)):
					cell_fmt = int_fmt
				elif isinstance(value, float):
					cell_fmt = num_fmt
				elif isinstance(value, datetime):
					cell_fmt = date_fmt
				worksheet.write(row_idx, col_idx, value, cell_fmt)

		worksheet.autofilter(0, 0, max(0, len(rows)), max(0, len(headers) - 1))
		worksheet.freeze_panes(1, 0)

		# ajusta ancho columnas
		for col in range(len(headers)):
			column_values = [str(headers[col])] + [str(r[col]) if r[col] is not None else "" for r in rows]
			max_len = min(max(len(v) for v in column_values) + 2, 60)
			worksheet.set_column(col, col, max_len)

		# cierra y devuelve bytes
		workbook.close()
		buffer.seek(0)
		return buffer.getvalue()

	@staticmethod
	def build_inventory_report(productos_queryset) -> bytes:
		# columnas del inventario
		headers = [
			"ID",
			"Nombre",
			"Categoría",
			"Precio",
			"Oferta Activa",
			"Precio Oferta",
			"Activo",
			"Ventas",
			"Stock",
			"Stock Mínimo",
			"Stock Máximo",
			"Estatus Stock",
			"Fecha Creación",
		]
		rows = []
		# recorre productos y arma filas
		for p in productos_queryset:
			inventario = getattr(p, "inventario", None)
			stock = getattr(inventario, "stock", 0) if inventario else 0
			stock_min = getattr(inventario, "stock_minimo", 0) if inventario else 0
			stock_max = getattr(inventario, "stock_maximo", 0) if inventario else 0
			status = "Bajo" if stock <= stock_min else ("Alto" if stock >= stock_max else "Óptimo")
			rows.append([
				p.id,
				p.nombre,
				getattr(p.categoria, "nombre", ""),
				float(p.precio or 0),
				"Sí" if p.oferta_activa else "No",
				float(p.precio_oferta or 0) if p.precio_oferta else None,
				"Sí" if p.activo else "No",
				int(p.ventas or 0),
				int(stock),
				int(stock_min),
				int(stock_max),
				status,
				p.fecha_creacion,
			])
		# crea el Excel
		return ExcelExportService.build_workbook(headers, rows, title="Inventario")

	@staticmethod
	def build_orders_report(pedidos_queryset) -> bytes:
		# columnas de pedidos
		headers = [
			"Número Pedido",
			"Fecha Pedido",
			"Cliente",
			"Email",
			"Estado",
			"Estado Pago",
			"Método Pago",
			"Total",
			"Ítems",
			"Dirección Envío",
		]
		rows = []
		# recorre pedidos y cuenta ítems
		for pedido in pedidos_queryset:
			cliente = pedido.get_datos_cliente()
			direccion = pedido.get_datos_envio().get("direccion_completa", "")
			items = sum(d.cantidad for d in pedido.detalles.all())
			rows.append([
				pedido.numero_pedido,
				pedido.fecha_pedido,
				cliente.get("nombre", ""),
				cliente.get("email", ""),
				pedido.estado,
				pedido.estado_pago,
				pedido.metodo_pago,
				float(pedido.total_pedido or 0),
				int(items),
				direccion,
			])
		# crea el Excel
		return ExcelExportService.build_workbook(headers, rows, title="Pedidos")


