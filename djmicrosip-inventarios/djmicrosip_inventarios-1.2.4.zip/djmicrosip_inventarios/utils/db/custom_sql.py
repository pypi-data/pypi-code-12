procedures = {}
procedures_fijos = []

procedures[ 'SIC_PUERTA_DEL_TRIGGERS' ] = '''
    CREATE OR ALTER PROCEDURE SIC_PUERTA_DEL_TRIGGERS 
    as
    begin
        if (exists(
            select 1 from RDB$Triggers
            where RDB$Trigger_name = 'SIC_PUERTA_INV_DOCTOSIN_BU')) then
            execute statement 'drop trigger SIC_PUERTA_INV_DOCTOSIN_BU';
    end
    '''

procedures[ 'SIC_ALMACENES_AT' ] = '''
    CREATE OR ALTER PROCEDURE SIC_ALMACENES_AT 
    as
    begin
        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'ALMACENES' and rf.RDB$FIELD_NAME = 'SIC_INVENTARIANDO')) then
            execute statement 'ALTER TABLE ALMACENES ADD SIC_INVENTARIANDO SMALLINT DEFAULT 1';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'ALMACENES' and rf.RDB$FIELD_NAME = 'SIC_INVCONAJUSTES')) then
            execute statement 'ALTER TABLE ALMACENES ADD SIC_INVCONAJUSTES SMALLINT DEFAULT 0';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'ALMACENES' and rf.RDB$FIELD_NAME = 'SIC_INVMODIFCOSTOS')) then
            execute statement 'ALTER TABLE ALMACENES ADD SIC_INVMODIFCOSTOS SMALLINT DEFAULT 0';
    end
    '''

procedures['SIC_DOCTOSINDET_AT'] = '''
    CREATE OR ALTER PROCEDURE SIC_DOCTOSINDET_AT
    as
    BEGIN

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_IN_DET' and rf.RDB$FIELD_NAME = 'SIC_FECHAHORA_U')) then
            execute statement 'ALTER TABLE DOCTOS_IN_DET ADD SIC_FECHAHORA_U FECHA_Y_HORA';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_IN_DET' and rf.RDB$FIELD_NAME = 'SIC_USUARIO_ULT_MODIF')) then
            execute statement 'ALTER TABLE DOCTOS_IN_DET ADD SIC_USUARIO_ULT_MODIF USUARIO_TYPE';

        if (not exists(
        select 1 from RDB$RELATION_FIELDS rf
        where rf.RDB$RELATION_NAME = 'DOCTOS_IN_DET' and rf.RDB$FIELD_NAME = 'SIC_DETALLETIME_MODIFICACIONES')) then
            execute statement 'ALTER TABLE DOCTOS_IN_DET ADD SIC_DETALLETIME_MODIFICACIONES MEMO';
    END
    '''

procedures['SIC_LOGINVENTARIO_VALINI_AT'] = '''
    CREATE OR ALTER PROCEDURE SIC_LOGINVENTARIO_VALINI_AT
    AS
    BEGIN
        IF (NOT EXISTS(
        SELECT 1 FROM RDB$RELATION_FIELDS RF
        WHERE RF.RDB$RELATION_NAME = 'SIC_LOGINVENTARIO_VALOR_INICIAL' AND RF.RDB$FIELD_NAME = 'EXISTENCIA_FINAL')) THEN
            EXECUTE STATEMENT 'ALTER TABLE SIC_LOGINVENTARIO_VALOR_INICIAL ADD EXISTENCIA_FINAL DECIMAL(18,5)';
    END
    '''

procedures_fijos.append({
    'name': 'SIC_GET_PRECIO_CON_IMPUESTO',
    'procedure': '''
        CREATE OR ALTER PROCEDURE SIC_GET_PRECIO_CON_IMPUESTO (
            articulo_id integer)
        returns (
            precio_con_impuesto numeric(18,6))
        as
        declare variable v_fpgc_unitario numeric(18,6);
        declare variable v_precio_lista numeric(18,6);
        BEGIN
            SELECT PA.PRECIO FROM ARTICULOS A JOIN PRECIOS_ARTICULOS PA ON PA.ARTICULO_ID = A.ARTICULO_ID
            JOIN PRECIOS_EMPRESA PE ON PE.PRECIO_EMPRESA_ID = PA.PRECIO_EMPRESA_ID
            WHERE ( PE.ID_INTERNO = 'L' ) AND A.ARTICULO_ID = :ARTICULO_ID
            INTO :V_PRECIO_LISTA;

            IF (V_PRECIO_LISTA IS NULL) THEN
                V_PRECIO_LISTA = 0;
            EXECUTE PROCEDURE PRECIO_CON_IMPTO(:ARTICULO_ID,:V_PRECIO_LISTA,'N',0,0,CURRENT_DATE, 'P')
            RETURNING_VALUES PRECIO_CON_IMPUESTO, V_FPGC_UNITARIO;
          SUSPEND;
        END
    '''
    })


