reports = {}
reports['Detalles Inventario Fisico - Costo'] = '''object ppReport: TppReport
  AutoStop = False
  DataPipeline = daFIBQueryDataView1.Log_Inventario_Fisico
  PrinterSetup.BinName = 'Default'
  PrinterSetup.DocumentName = 'Report'
  PrinterSetup.PaperName = 'Letter'
  PrinterSetup.PrinterName = 'Default'
  PrinterSetup.mmMarginBottom = 6350
  PrinterSetup.mmMarginLeft = 6350
  PrinterSetup.mmMarginRight = 6350
  PrinterSetup.mmMarginTop = 6350
  PrinterSetup.mmPaperHeight = 279401
  PrinterSetup.mmPaperWidth = 215900
  PrinterSetup.PaperSize = 1
  SaveAsTemplate = True
  Template.DatabaseSettings.DataPipeline = plRBItem
  Template.DatabaseSettings.Name = 'Detalles Inventario Fisico - Costo'
  Template.DatabaseSettings.NameField = 'NAME'
  Template.DatabaseSettings.TemplateField = 'TEMPLATE'
  Template.SaveTo = stDatabase
  Template.Format = ftASCII
  Units = utScreenPixels
  AllowPrintToFile = True
  DeviceType = 'Screen'
  EmailSettings.ReportFormat = 'PDF'
  Language = lgSpanishMexico
  OutlineSettings.CreateNode = True
  OutlineSettings.CreatePageNodes = True
  OutlineSettings.Enabled = False
  OutlineSettings.Visible = False
  TextSearchSettings.DefaultString = '<HallarTexto>'
  TextSearchSettings.Enabled = False
  Left = 4
  Top = 208
  Version = '10.08'
  mmColumnWidth = 0
  DataPipelineName = 'Log_Inventario_Fisico'
  object ppHeaderBand1: TppHeaderBand
    mmBottomOffset = 0
    mmHeight = 13494
    mmPrintPosition = 0
    object ppLabel5: TppLabel
      UserName = 'Label5'
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      Caption = 'Detalle de inventario fisico - Costo'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clBlack
      Font.Name = 'Arial'
      Font.Size = 14
      Font.Style = [fsBold]
      Transparent = True
      mmHeight = 5821
      mmLeft = 44715
      mmTop = 265
      mmWidth = 104511
      BandType = 0
    end
    object ppLabel1: TppLabel
      UserName = 'Label1'
      AutoSize = False
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      Caption = 'Articulo'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 10
      Font.Style = [fsBold]
      Transparent = True
      mmHeight = 4191
      mmLeft = 1323
      mmTop = 9260
      mmWidth = 19315
      BandType = 0
    end
    object ppLabel2: TppLabel
      UserName = 'Label2'
      AutoSize = False
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      Caption = 'Inicial'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 10
      Font.Style = [fsBold]
      TextAlignment = taRightJustified
      Transparent = True
      mmHeight = 4191
      mmLeft = 78052
      mmTop = 9260
      mmWidth = 13494
      BandType = 0
    end
    object ppLabel3: TppLabel
      UserName = 'Label3'
      AutoSize = False
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      Caption = 'Final'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 10
      Font.Style = [fsBold]
      TextAlignment = taRightJustified
      Transparent = True
      mmHeight = 4191
      mmLeft = 102923
      mmTop = 9260
      mmWidth = 15610
      BandType = 0
    end
    object ppLabel4: TppLabel
      UserName = 'Label4'
      AutoSize = False
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      Caption = 'Diferencia'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 10
      Font.Style = [fsBold]
      TextAlignment = taRightJustified
      Transparent = True
      mmHeight = 4191
      mmLeft = 120915
      mmTop = 9260
      mmWidth = 23019
      BandType = 0
    end
    object ppLabel6: TppLabel
      UserName = 'Label6'
      AutoSize = False
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      Caption = 'Precio Venta'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 10
      Font.Style = [fsBold]
      TextAlignment = taRightJustified
      Transparent = True
      mmHeight = 4191
      mmLeft = 147638
      mmTop = 9260
      mmWidth = 21431
      BandType = 0
    end
    object ppLabel7: TppLabel
      UserName = 'Label7'
      AutoSize = False
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      Caption = 'Diferencia $'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 10
      Font.Style = [fsBold]
      TextAlignment = taRightJustified
      Transparent = True
      mmHeight = 4191
      mmLeft = 179123
      mmTop = 9260
      mmWidth = 21431
      BandType = 0
    end
  end
  object ppDetailBand1: TppDetailBand
    mmBottomOffset = 0
    mmHeight = 3175
    mmPrintPosition = 0
    object ppDBText1: TppDBText
      UserName = 'DBText1'
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      DataField = 'NOMBRE'
      DataPipeline = daFIBQueryDataView1.Log_Inventario_Fisico
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 8
      Font.Style = []
      Transparent = True
      DataPipelineName = 'Log_Inventario_Fisico'
      mmHeight = 3175
      mmLeft = 1323
      mmTop = 0
      mmWidth = 65881
      BandType = 4
    end
    object ppDBText2: TppDBText
      UserName = 'DBText2'
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      DataField = 'EXISTENCIA_INICIAL'
      DataPipeline = daFIBQueryDataView1.Log_Inventario_Fisico
      DisplayFormat = '#,0.00;-#,0.00'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 8
      Font.Style = []
      TextAlignment = taRightJustified
      Transparent = True
      DataPipelineName = 'Log_Inventario_Fisico'
      mmHeight = 3175
      mmLeft = 69586
      mmTop = 0
      mmWidth = 21960
      BandType = 4
    end
    object ppDBText3: TppDBText
      UserName = 'DBText3'
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      DataField = 'EXISTENCIA_FINAL'
      DataPipeline = daFIBQueryDataView1.Log_Inventario_Fisico
      DisplayFormat = '#,0.00;-#,0.00'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 8
      Font.Style = []
      TextAlignment = taRightJustified
      Transparent = True
      DataPipelineName = 'Log_Inventario_Fisico'
      mmHeight = 3260
      mmLeft = 97367
      mmTop = 0
      mmWidth = 21167
      BandType = 4
    end
    object ppDBText4: TppDBText
      UserName = 'DBText4'
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      DataField = 'COSTO'
      DataPipeline = daFIBQueryDataView1.Log_Inventario_Fisico
      DisplayFormat = '$#,0.00;-$#,0.00'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 8
      Font.Style = []
      TextAlignment = taRightJustified
      Transparent = True
      DataPipelineName = 'Log_Inventario_Fisico'
      mmHeight = 3175
      mmLeft = 152929
      mmTop = 0
      mmWidth = 16140
      BandType = 4
    end
    object ppDBText5: TppDBText
      UserName = 'DBText5'
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      DataField = 'DIFERENCIA'
      DataPipeline = daFIBQueryDataView1.Log_Inventario_Fisico
      DisplayFormat = '#,0.00;-#,0.00'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 8
      Font.Style = []
      TextAlignment = taRightJustified
      Transparent = True
      DataPipelineName = 'Log_Inventario_Fisico'
      mmHeight = 3175
      mmLeft = 127265
      mmTop = 0
      mmWidth = 16669
      BandType = 4
    end
    object ppDBText6: TppDBText
      UserName = 'DBText6'
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      DataField = 'DIFERENCIA_DINERO'
      DataPipeline = daFIBQueryDataView1.Log_Inventario_Fisico
      DisplayFormat = '$#,0.00;-$#,0.00'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 8
      Font.Style = []
      TextAlignment = taRightJustified
      Transparent = True
      DataPipelineName = 'Log_Inventario_Fisico'
      mmHeight = 3175
      mmLeft = 173302
      mmTop = 0
      mmWidth = 27252
      BandType = 4
    end
  end
  object ppFooterBand1: TppFooterBand
    mmBottomOffset = 0
    mmHeight = 0
    mmPrintPosition = 0
  end
  object ppSummaryBand1: TppSummaryBand
    mmBottomOffset = 0
    mmHeight = 6085
    mmPrintPosition = 0
    object ppDBCalc1: TppDBCalc
      UserName = 'DBCalc1'
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      DataField = 'DIFERENCIA_DINERO'
      DataPipeline = daFIBQueryDataView1.Log_Inventario_Fisico
      DisplayFormat = '$#,0.00;-$#,0.00'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 10
      Font.Style = []
      TextAlignment = taRightJustified
      Transparent = True
      DataPipelineName = 'Log_Inventario_Fisico'
      mmHeight = 4022
      mmLeft = 175419
      mmTop = 1852
      mmWidth = 26194
      BandType = 7
    end
    object ppLabel8: TppLabel
      UserName = 'Label8'
      AutoSize = False
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      Caption = 'Total Diferencia'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 10
      Font.Style = [fsBold]
      TextAlignment = taRightJustified
      Transparent = True
      mmHeight = 4233
      mmLeft = 136261
      mmTop = 1852
      mmWidth = 31750
      BandType = 7
    end
  end
  object raCodeModule1: TraCodeModule
    ProgramStream = {
      01060F5472614576656E7448616E646C65720B50726F6772616D4E616D65060E
      444254657874364F6E5072696E740B50726F6772616D54797065070B74745072
      6F63656475726506536F7572636506EC70726F63656475726520444254657874
      364F6E5072696E743B0D0A626567696E0D0A20202020696620284C6F675F496E
      76656E746172696F5F46697369636F5B274449464552454E4349415F44494E45
      524F275D203C203029207468656E0D0A20202020626567696E0D0A2020202020
      202020444254657874362E466F6E742E436F6C6F72203A3D20636C5265643B0D
      0A20202020656E640D0A20202020656C73650D0A20202020626567696E0D0A20
      20202020202020444254657874362E466F6E742E436F6C6F72203A3D20636C57
      696E646F77546578743B0D0A20202020656E643B0D0A656E643B0D0A0D436F6D
      706F6E656E744E616D65060744425465787436094576656E744E616D6506074F
      6E5072696E74074576656E74494402200001060F5472614576656E7448616E64
      6C65720B50726F6772616D4E616D65060E444243616C63314F6E5072696E740B
      50726F6772616D54797065070B747450726F63656475726506536F7572636506
      CD70726F63656475726520444243616C63314F6E5072696E743B0D0A62656769
      6E0D0A202069662028444243616C63312E56616C7565203C203029207468656E
      0D0A20202020626567696E0D0A2020202020202020444243616C63312E466F6E
      742E436F6C6F72203A3D20636C5265643B0D0A20202020656E640D0A20202020
      656C73650D0A20202020626567696E0D0A2020202020202020444243616C6331
      2E466F6E742E436F6C6F72203A3D20636C57696E646F77546578743B0D0A2020
      2020656E643B0D0A656E643B0D0A0D436F6D706F6E656E744E616D6506074442
      43616C6331094576656E744E616D6506074F6E5072696E74074576656E744944
      02200000}
  end
  object daDataModule1: TdaDataModule
    object daFIBQueryDataView1: TdaFIBQueryDataView
      UserName = 'Query_Log_Inventario_Fisico'
      Height = 298
      Left = 10
      NameColumnWidth = 105
      SizeColumnWidth = 35
      SortMode = 0
      Top = 10
      TypeColumnWidth = 52
      Width = 373
      AutoSearchTabOrder = 0
      object Log_Inventario_Fisico: TppChildDBPipeline
        AutoCreateFields = False
        UserName = 'Log_Inventario_Fisico'
        object ppField1: TppField
          FieldAlias = 'ARTICULO_ID'
          FieldName = 'ARTICULO_ID'
          FieldLength = 0
          DataType = dtInteger
          DisplayWidth = 10
          Position = 0
        end
        object ppField2: TppField
          FieldAlias = 'NOMBRE'
          FieldName = 'NOMBRE'
          FieldLength = 100
          DisplayWidth = 100
          Position = 1
        end
        object ppField3: TppField
          FieldAlias = 'EXISTENCIA_INICIAL'
          FieldName = 'EXISTENCIA_INICIAL'
          FieldLength = 0
          DataType = dtDouble
          DisplayWidth = 10
          Position = 2
        end
        object ppField4: TppField
          FieldAlias = 'EXISTENCIA_FINAL'
          FieldName = 'EXISTENCIA_FINAL'
          FieldLength = 0
          DataType = dtDouble
          DisplayWidth = 10
          Position = 3
        end
        object ppField5: TppField
          FieldAlias = 'COSTO'
          FieldName = 'COSTO'
          FieldLength = 0
          DataType = dtDouble
          DisplayWidth = 10
          Position = 4
        end
        object ppField6: TppField
          FieldAlias = 'DIFERENCIA'
          FieldName = 'DIFERENCIA'
          FieldLength = 0
          DataType = dtDouble
          DisplayWidth = 10
          Position = 5
        end
        object ppField7: TppField
          FieldAlias = 'DIFERENCIA_DINERO'
          FieldName = 'DIFERENCIA_DINERO'
          FieldLength = 0
          DataType = dtDouble
          DisplayWidth = 10
          Position = 6
        end
      end
      object daSQL1: TdaSQL
        CollationType = ctASCII
        DatabaseName = 'dtbsMicrosip'
        DatabaseType = dtInterBase
        DataPipelineName = 'Log_Inventario_Fisico'
        EditSQLAsText = True
        IsCaseSensitive = True
        LinkColor = clBlack
        MaxSQLFieldAliasLength = 0
        SQLText.Strings = (
          
            'SELECT ARTICULO_ID, NOMBRE,  EXISTENCIA_INICIAL,  EXISTENCIA_FIN' +
            'AL, COSTO,'
          ' (EXISTENCIA_FINAL - EXISTENCIA_INICIAL) AS DIFERENCIA,'
          
            ' ((EXISTENCIA_FINAL - EXISTENCIA_INICIAL) * COSTO) AS DIFERENCIA' +
            '_DINERO'
          'FROM'
          '(SELECT ARTICULOS_1.ARTICULO_ID, ARTICULOS_1.NOMBRE, '
          
            '       SIC_LOGINVENTARIO_VALOR_INICIAL_1.EXISTENCIA AS EXISTENCI' +
            'A_INICIAL, '
          
            '       SIC_LOGINVENTARIO_VALOR_INICIAL_1.EXISTENCIA_FINAL AS EXI' +
            'STENCIA_FINAL,'
          '       ARTICULOS_1.COSTO_ULTIMA_COMPRA AS COSTO'
          'FROM SIC_LOGINVENTARIO SIC_LOGINVENTARIO_1'
          
            '      INNER JOIN SIC_LOGINVENTARIO_VALOR_INICIAL SIC_LOGINVENTAR' +
            'IO_VALOR_INICIAL_1 ON '
          
            '     (SIC_LOGINVENTARIO_VALOR_INICIAL_1.LOG_INVENTARIO_ID = SIC_' +
            'LOGINVENTARIO_1.ID)'
          '      INNER JOIN ARTICULOS ARTICULOS_1 ON '
          
            '     (ARTICULOS_1.ARTICULO_ID = SIC_LOGINVENTARIO_VALOR_INICIAL_' +
            '1.ARTICULO_ID)'
          '      INNER JOIN ALMACENES ALMACENES_1 ON '
          '     (ALMACENES_1.ALMACEN_ID = SIC_LOGINVENTARIO_1.ALMACEN_ID)'
          'WHERE SIC_LOGINVENTARIO_1.ID= :INVENTARIO_LOG_ID)')
        SQLType = sqSQL2
        object daField1: TdaField
          Alias = 'ARTICULO_ID'
          DataType = dtInteger
          DisplayWidth = 10
          FieldAlias = 'ARTICULO_ID'
          FieldLength = 0
          FieldName = 'ARTICULO_ID'
          SQLFieldName = 'ARTICULO_ID'
        end
        object daField2: TdaField
          Alias = 'NOMBRE'
          DisplayWidth = 100
          FieldAlias = 'NOMBRE'
          FieldLength = 100
          FieldName = 'NOMBRE'
          SQLFieldName = 'NOMBRE'
        end
        object daField3: TdaField
          Alias = 'EXISTENCIA_INICIAL'
          DataType = dtDouble
          DisplayWidth = 10
          FieldAlias = 'EXISTENCIA_INICIAL'
          FieldLength = 0
          FieldName = 'EXISTENCIA_INICIAL'
          SQLFieldName = 'EXISTENCIA_INICIAL'
        end
        object daField4: TdaField
          Alias = 'EXISTENCIA_FINAL'
          DataType = dtDouble
          DisplayWidth = 10
          FieldAlias = 'EXISTENCIA_FINAL'
          FieldLength = 0
          FieldName = 'EXISTENCIA_FINAL'
          SQLFieldName = 'EXISTENCIA_FINAL'
        end
        object daField5: TdaField
          Alias = 'COSTO'
          DataType = dtDouble
          DisplayWidth = 10
          FieldAlias = 'COSTO'
          FieldLength = 0
          FieldName = 'COSTO'
          SQLFieldName = 'COSTO'
        end
        object daField6: TdaField
          Alias = 'DIFERENCIA'
          DataType = dtDouble
          DisplayWidth = 10
          FieldAlias = 'DIFERENCIA'
          FieldLength = 0
          FieldName = 'DIFERENCIA'
          SQLFieldName = 'DIFERENCIA'
        end
        object daField7: TdaField
          Alias = 'DIFERENCIA_DINERO'
          DataType = dtDouble
          DisplayWidth = 10
          FieldAlias = 'DIFERENCIA_DINERO'
          FieldLength = 0
          FieldName = 'DIFERENCIA_DINERO'
          SQLFieldName = 'DIFERENCIA_DINERO'
        end
      end
    end
  end
  object ppParameterList1: TppParameterList
  end
end
'''

reports['Detalles Inventario Fisico - Precio de Venta'] = '''object ppReport: TppReport
  AutoStop = False
  DataPipeline = daFIBQueryDataView1.Log_Inventario_Fisico
  PrinterSetup.BinName = 'Default'
  PrinterSetup.DocumentName = 'Report'
  PrinterSetup.PaperName = 'Letter'
  PrinterSetup.PrinterName = 'Default'
  PrinterSetup.mmMarginBottom = 6350
  PrinterSetup.mmMarginLeft = 6350
  PrinterSetup.mmMarginRight = 6350
  PrinterSetup.mmMarginTop = 6350
  PrinterSetup.mmPaperHeight = 279401
  PrinterSetup.mmPaperWidth = 215900
  PrinterSetup.PaperSize = 1
  SaveAsTemplate = True
  Template.DatabaseSettings.DataPipeline = plRBItem
  Template.DatabaseSettings.Name = 'Detalles Inventario Fisico - Precio de Venta'
  Template.DatabaseSettings.NameField = 'NAME'
  Template.DatabaseSettings.TemplateField = 'TEMPLATE'
  Template.SaveTo = stDatabase
  Template.Format = ftASCII
  Units = utScreenPixels
  AllowPrintToFile = True
  DeviceType = 'Screen'
  EmailSettings.ReportFormat = 'PDF'
  Language = lgSpanishMexico
  OutlineSettings.CreateNode = True
  OutlineSettings.CreatePageNodes = True
  OutlineSettings.Enabled = False
  OutlineSettings.Visible = False
  TextSearchSettings.DefaultString = '<HallarTexto>'
  TextSearchSettings.Enabled = False
  Left = 4
  Top = 208
  Version = '10.08'
  mmColumnWidth = 0
  DataPipelineName = 'Log_Inventario_Fisico'
  object ppHeaderBand1: TppHeaderBand
    mmBottomOffset = 0
    mmHeight = 13494
    mmPrintPosition = 0
    object ppLabel1: TppLabel
      UserName = 'Label1'
      AutoSize = False
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      Caption = 'Articulo'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 10
      Font.Style = [fsBold]
      Transparent = True
      mmHeight = 4191
      mmLeft = 1323
      mmTop = 9260
      mmWidth = 19315
      BandType = 0
    end
    object ppLabel2: TppLabel
      UserName = 'Label2'
      AutoSize = False
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      Caption = 'Inicial'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 10
      Font.Style = [fsBold]
      TextAlignment = taRightJustified
      Transparent = True
      mmHeight = 4191
      mmLeft = 78052
      mmTop = 9260
      mmWidth = 13494
      BandType = 0
    end
    object ppLabel3: TppLabel
      UserName = 'Label3'
      AutoSize = False
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      Caption = 'Final'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 10
      Font.Style = [fsBold]
      TextAlignment = taRightJustified
      Transparent = True
      mmHeight = 4191
      mmLeft = 102923
      mmTop = 9260
      mmWidth = 15610
      BandType = 0
    end
    object ppLabel4: TppLabel
      UserName = 'Label4'
      AutoSize = False
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      Caption = 'Diferencia'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 10
      Font.Style = [fsBold]
      TextAlignment = taRightJustified
      Transparent = True
      mmHeight = 4191
      mmLeft = 120915
      mmTop = 9260
      mmWidth = 23019
      BandType = 0
    end
    object ppLabel5: TppLabel
      UserName = 'Label5'
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      Caption = 'Detalle de inventario fisico - Precio de venta'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clBlack
      Font.Name = 'Arial'
      Font.Size = 14
      Font.Style = [fsBold]
      Transparent = True
      mmHeight = 5821
      mmLeft = 44715
      mmTop = 265
      mmWidth = 108479
      BandType = 0
    end
    object ppLabel6: TppLabel
      UserName = 'Label6'
      AutoSize = False
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      Caption = 'Precio Venta'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 10
      Font.Style = [fsBold]
      TextAlignment = taRightJustified
      Transparent = True
      mmHeight = 4191
      mmLeft = 147638
      mmTop = 9260
      mmWidth = 21431
      BandType = 0
    end
    object ppLabel7: TppLabel
      UserName = 'Label7'
      AutoSize = False
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      Caption = 'Diferencia $'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 10
      Font.Style = [fsBold]
      TextAlignment = taRightJustified
      Transparent = True
      mmHeight = 4191
      mmLeft = 179123
      mmTop = 9260
      mmWidth = 21431
      BandType = 0
    end
  end
  object ppDetailBand1: TppDetailBand
    mmBottomOffset = 0
    mmHeight = 3175
    mmPrintPosition = 0
    object ppDBText1: TppDBText
      UserName = 'DBText1'
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      DataField = 'NOMBRE'
      DataPipeline = daFIBQueryDataView1.Log_Inventario_Fisico
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 8
      Font.Style = []
      Transparent = True
      DataPipelineName = 'Log_Inventario_Fisico'
      mmHeight = 3175
      mmLeft = 1323
      mmTop = 0
      mmWidth = 65881
      BandType = 4
    end
    object ppDBText2: TppDBText
      UserName = 'DBText2'
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      DataField = 'EXISTENCIA_INICIAL'
      DataPipeline = daFIBQueryDataView1.Log_Inventario_Fisico
      DisplayFormat = '#,0.00;-#,0.00'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 8
      Font.Style = []
      TextAlignment = taRightJustified
      Transparent = True
      DataPipelineName = 'Log_Inventario_Fisico'
      mmHeight = 3175
      mmLeft = 69586
      mmTop = 0
      mmWidth = 21960
      BandType = 4
    end
    object ppDBText3: TppDBText
      UserName = 'DBText3'
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      DataField = 'EXISTENCIA_FINAL'
      DataPipeline = daFIBQueryDataView1.Log_Inventario_Fisico
      DisplayFormat = '#,0.00;-#,0.00'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 8
      Font.Style = []
      TextAlignment = taRightJustified
      Transparent = True
      DataPipelineName = 'Log_Inventario_Fisico'
      mmHeight = 3260
      mmLeft = 97367
      mmTop = 0
      mmWidth = 21167
      BandType = 4
    end
    object ppDBText4: TppDBText
      UserName = 'DBText4'
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      DataField = 'PRECIO'
      DataPipeline = daFIBQueryDataView1.Log_Inventario_Fisico
      DisplayFormat = '$#,0.00;-$#,0.00'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 8
      Font.Style = []
      TextAlignment = taRightJustified
      Transparent = True
      DataPipelineName = 'Log_Inventario_Fisico'
      mmHeight = 3175
      mmLeft = 152929
      mmTop = 0
      mmWidth = 16140
      BandType = 4
    end
    object ppDBText5: TppDBText
      UserName = 'DBText5'
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      DataField = 'DIFERENCIA'
      DataPipeline = daFIBQueryDataView1.Log_Inventario_Fisico
      DisplayFormat = '#,0.00;-#,0.00'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 8
      Font.Style = []
      TextAlignment = taRightJustified
      Transparent = True
      DataPipelineName = 'Log_Inventario_Fisico'
      mmHeight = 3175
      mmLeft = 127265
      mmTop = 0
      mmWidth = 16669
      BandType = 4
    end
    object ppDBText6: TppDBText
      UserName = 'DBText6'
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      DataField = 'DIFERENCIA_DINERO'
      DataPipeline = daFIBQueryDataView1.Log_Inventario_Fisico
      DisplayFormat = '$#,0.00;-$#,0.00'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 8
      Font.Style = []
      TextAlignment = taRightJustified
      Transparent = True
      DataPipelineName = 'Log_Inventario_Fisico'
      mmHeight = 3175
      mmLeft = 173302
      mmTop = 0
      mmWidth = 27252
      BandType = 4
    end
  end
  object ppFooterBand1: TppFooterBand
    mmBottomOffset = 0
    mmHeight = 0
    mmPrintPosition = 0
  end
  object ppSummaryBand1: TppSummaryBand
    mmBottomOffset = 0
    mmHeight = 6085
    mmPrintPosition = 0
    object ppDBCalc1: TppDBCalc
      UserName = 'DBCalc1'
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      DataField = 'DIFERENCIA_DINERO'
      DataPipeline = daFIBQueryDataView1.Log_Inventario_Fisico
      DisplayFormat = '$#,0.00;-$#,0.00'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 10
      Font.Style = []
      TextAlignment = taRightJustified
      Transparent = True
      DataPipelineName = 'Log_Inventario_Fisico'
      mmHeight = 4022
      mmLeft = 175419
      mmTop = 1852
      mmWidth = 26194
      BandType = 7
    end
    object ppLabel8: TppLabel
      UserName = 'Label8'
      AutoSize = False
      Border.BorderPositions = []
      Border.Color = clBlack
      Border.Style = psSolid
      Border.Visible = False
      Caption = 'Total Diferencia'
      Font.Charset = DEFAULT_CHARSET
      Font.Color = clWindowText
      Font.Name = 'Arial'
      Font.Size = 10
      Font.Style = [fsBold]
      TextAlignment = taRightJustified
      Transparent = True
      mmHeight = 4233
      mmLeft = 136261
      mmTop = 1852
      mmWidth = 31750
      BandType = 7
    end
  end
  object raCodeModule1: TraCodeModule
    ProgramStream = {
      01060F5472614576656E7448616E646C65720B50726F6772616D4E616D65060E
      444254657874364F6E5072696E740B50726F6772616D54797065070B74745072
      6F63656475726506536F7572636506EC70726F63656475726520444254657874
      364F6E5072696E743B0D0A626567696E0D0A20202020696620284C6F675F496E
      76656E746172696F5F46697369636F5B274449464552454E4349415F44494E45
      524F275D203C203029207468656E0D0A20202020626567696E0D0A2020202020
      202020444254657874362E466F6E742E436F6C6F72203A3D20636C5265643B0D
      0A20202020656E640D0A20202020656C73650D0A20202020626567696E0D0A20
      20202020202020444254657874362E466F6E742E436F6C6F72203A3D20636C57
      696E646F77546578743B0D0A20202020656E643B0D0A656E643B0D0A0D436F6D
      706F6E656E744E616D65060744425465787436094576656E744E616D6506074F
      6E5072696E74074576656E74494402200001060F5472614576656E7448616E64
      6C65720B50726F6772616D4E616D65060E444243616C63314F6E5072696E740B
      50726F6772616D54797065070B747450726F63656475726506536F7572636506
      CD70726F63656475726520444243616C63314F6E5072696E743B0D0A62656769
      6E0D0A202069662028444243616C63312E56616C7565203C203029207468656E
      0D0A20202020626567696E0D0A2020202020202020444243616C63312E466F6E
      742E436F6C6F72203A3D20636C5265643B0D0A20202020656E640D0A20202020
      656C73650D0A20202020626567696E0D0A2020202020202020444243616C6331
      2E466F6E742E436F6C6F72203A3D20636C57696E646F77546578743B0D0A2020
      2020656E643B0D0A656E643B0D0A0D436F6D706F6E656E744E616D6506074442
      43616C6331094576656E744E616D6506074F6E5072696E74074576656E744944
      02200000}
  end
  object daDataModule1: TdaDataModule
    object daFIBQueryDataView1: TdaFIBQueryDataView
      UserName = 'Query_Log_Inventario_Fisico'
      Height = 298
      Left = 10
      NameColumnWidth = 105
      SizeColumnWidth = 35
      SortMode = 0
      Top = 10
      TypeColumnWidth = 52
      Width = 373
      AutoSearchTabOrder = 0
      object Log_Inventario_Fisico: TppChildDBPipeline
        AutoCreateFields = False
        UserName = 'Log_Inventario_Fisico'
        object ppField1: TppField
          FieldAlias = 'ARTICULO_ID'
          FieldName = 'ARTICULO_ID'
          FieldLength = 0
          DataType = dtInteger
          DisplayWidth = 10
          Position = 0
        end
        object ppField2: TppField
          FieldAlias = 'NOMBRE'
          FieldName = 'NOMBRE'
          FieldLength = 100
          DisplayWidth = 100
          Position = 1
        end
        object ppField3: TppField
          FieldAlias = 'EXISTENCIA_INICIAL'
          FieldName = 'EXISTENCIA_INICIAL'
          FieldLength = 0
          DataType = dtDouble
          DisplayWidth = 10
          Position = 2
        end
        object ppField4: TppField
          FieldAlias = 'EXISTENCIA_FINAL'
          FieldName = 'EXISTENCIA_FINAL'
          FieldLength = 0
          DataType = dtDouble
          DisplayWidth = 10
          Position = 3
        end
        object ppField5: TppField
          FieldAlias = 'PRECIO'
          FieldName = 'PRECIO'
          FieldLength = 0
          DataType = dtDouble
          DisplayWidth = 10
          Position = 4
        end
        object ppField6: TppField
          FieldAlias = 'DIFERENCIA'
          FieldName = 'DIFERENCIA'
          FieldLength = 0
          DataType = dtDouble
          DisplayWidth = 10
          Position = 5
        end
        object ppField7: TppField
          FieldAlias = 'DIFERENCIA_DINERO'
          FieldName = 'DIFERENCIA_DINERO'
          FieldLength = 0
          DataType = dtDouble
          DisplayWidth = 10
          Position = 6
        end
      end
      object daSQL1: TdaSQL
        CollationType = ctASCII
        DatabaseName = 'dtbsMicrosip'
        DatabaseType = dtInterBase
        DataPipelineName = 'Log_Inventario_Fisico'
        EditSQLAsText = True
        IsCaseSensitive = True
        LinkColor = clBlack
        MaxSQLFieldAliasLength = 0
        SQLText.Strings = (
          
            'SELECT ARTICULO_ID, NOMBRE,  existencia_inicial,  existencia_fin' +
            'al, PRECIO,'
          ' (existencia_final - existencia_inicial) as DIFERENCIA,'
          
            ' ((existencia_final - existencia_inicial) * PRECIO) AS DIFERENCI' +
            'A_DINERO'
          'FROM'
          '(SELECT ARTICULOS_1.ARTICULO_ID, ARTICULOS_1.NOMBRE, '
          
            '       SIC_LOGINVENTARIO_VALOR_INICIAL_1.EXISTENCIA as existenci' +
            'a_inicial, '
          
            '       SIC_LOGINVENTARIO_VALOR_INICIAL_1.EXISTENCIA_FINAL as exi' +
            'stencia_final,'
          
            '(SELECT PRECIO_CON_IMPUESTO FROM SIC_GET_PRECIO_CON_IMPUESTO(ART' +
            'ICULOS_1.ARTICULO_ID)) AS PRECIO'
          'FROM SIC_LOGINVENTARIO SIC_LOGINVENTARIO_1'
          
            '      INNER JOIN SIC_LOGINVENTARIO_VALOR_INICIAL SIC_LOGINVENTAR' +
            'IO_VALOR_INICIAL_1 ON '
          
            '     (SIC_LOGINVENTARIO_VALOR_INICIAL_1.LOG_INVENTARIO_ID = SIC_' +
            'LOGINVENTARIO_1.ID)'
          '      INNER JOIN ARTICULOS ARTICULOS_1 ON '
          
            '     (ARTICULOS_1.ARTICULO_ID = SIC_LOGINVENTARIO_VALOR_INICIAL_' +
            '1.ARTICULO_ID)'
          '      INNER JOIN ALMACENES ALMACENES_1 ON '
          '     (ALMACENES_1.ALMACEN_ID = SIC_LOGINVENTARIO_1.ALMACEN_ID)'
          'where SIC_LOGINVENTARIO_1.id= :inventario_log_id) ')
        SQLType = sqSQL2
        object daField1: TdaField
          Alias = 'ARTICULO_ID'
          DataType = dtInteger
          DisplayWidth = 10
          FieldAlias = 'ARTICULO_ID'
          FieldLength = 0
          FieldName = 'ARTICULO_ID'
          SQLFieldName = 'ARTICULO_ID'
        end
        object daField2: TdaField
          Alias = 'NOMBRE'
          DisplayWidth = 100
          FieldAlias = 'NOMBRE'
          FieldLength = 100
          FieldName = 'NOMBRE'
          SQLFieldName = 'NOMBRE'
        end
        object daField3: TdaField
          Alias = 'EXISTENCIA_INICIAL'
          DataType = dtDouble
          DisplayWidth = 10
          FieldAlias = 'EXISTENCIA_INICIAL'
          FieldLength = 0
          FieldName = 'EXISTENCIA_INICIAL'
          SQLFieldName = 'EXISTENCIA_INICIAL'
        end
        object daField4: TdaField
          Alias = 'EXISTENCIA_FINAL'
          DataType = dtDouble
          DisplayWidth = 10
          FieldAlias = 'EXISTENCIA_FINAL'
          FieldLength = 0
          FieldName = 'EXISTENCIA_FINAL'
          SQLFieldName = 'EXISTENCIA_FINAL'
        end
        object daField5: TdaField
          Alias = 'PRECIO'
          DataType = dtDouble
          DisplayWidth = 10
          FieldAlias = 'PRECIO'
          FieldLength = 0
          FieldName = 'PRECIO'
          SQLFieldName = 'PRECIO'
        end
        object daField6: TdaField
          Alias = 'DIFERENCIA'
          DataType = dtDouble
          DisplayWidth = 10
          FieldAlias = 'DIFERENCIA'
          FieldLength = 0
          FieldName = 'DIFERENCIA'
          SQLFieldName = 'DIFERENCIA'
        end
        object daField7: TdaField
          Alias = 'DIFERENCIA_DINERO'
          DataType = dtDouble
          DisplayWidth = 10
          FieldAlias = 'DIFERENCIA_DINERO'
          FieldLength = 0
          FieldName = 'DIFERENCIA_DINERO'
          SQLFieldName = 'DIFERENCIA_DINERO'
        end
      end
    end
  end
  object ppParameterList1: TppParameterList
  end
end
'''
